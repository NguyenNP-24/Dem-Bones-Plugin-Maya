#include "demBonesCmd.h"

#include <string>
#include <sstream>
#include <vector>
#include <map>

#include <maya/MFnSkinCluster.h>
#include <maya/MFnMatrixData.h>
#include <maya/MFnAnimCurve.h>

#include <maya/MTime.h>
#include <maya/MIntArray.h>
#include <maya/MFloatArray.h>
#include <maya/MQuaternion.h>
#include <maya/MEulerRotation.h>
#include <maya/MSelectionList.h>
#include <maya/MAnimControl.h>

#include <Eigen/Dense>
#include <DemBones/MatBlocks.h>

#include "mayautils/dgUtils.h"
#include "mayautils/dagUtils.h"
#include "mayautils/skinUtils.h"

MString DemBonesCmd::typeName("demBones");

static const char kSourcedFlag[]{ "src" };
static const char kSourcedFlagLong[]{ "sourceMesh" };
static const char kTargetFlag[]{ "trg" };
static const char kTargetFlagLong[]{ "targetMesh" };

static const char kJointsFlag[]{"jnt"};
static const char kJointsFlagLong[]{"joints"};

static const char kStartFrameFlag[]{ "sta" };
static const char kStartFrameFlagLong[]{ "startFrame" };
static const char kEndFrameFlag[]{ "end" };
static const char kEndFrameFlagLong[]{ "endFrame" };

static const char kGlobalItersFlag[]{ "git" };
static const char kGlobalItersFlagLong[]{ "globalIters" };
static const char kWeightsItersFlag[]{ "wit" };
static const char kWeightsItersFlagLong[]{ "weightIters" };
static const char kTransItersFlag[]{ "tit" };
static const char kTransItersFlagLong[]{ "transIters" };

static const char kNumBonesFlag[]{ "nb" };
static const char kNumBonesFlagLong[]{ "numBones" };

static const char kDefaultJointName[] = "joint";

static const char kPatienceFlag[]{ "pt" };
static const char kPatienceFlagLong[]{ "patience" };
static const char kToleranceFlag[]{ "tl" };
static const char kToleranceFlagLong[]{ "tolerance" };

static const char kReuseSkeletonFlag[]{ "rs" };
static const char kReuseSkeletonFlagLong[]{ "reuseSkeleton" };

DemBonesCmd::DemBonesCmd():
	MPxCommand()
{
	;
}

DemBonesCmd::~DemBonesCmd()
{
	;
}

MSyntax DemBonesCmd::createSyntax()
{
	MStatus status;
	MSyntax syntax;
	syntax.addFlag(kGlobalItersFlag, kGlobalItersFlagLong, MSyntax::kLong);
	syntax.addFlag(kWeightsItersFlag, kWeightsItersFlagLong, MSyntax::kLong);
	syntax.addFlag(kTransItersFlag, kTransItersFlagLong, MSyntax::kLong);
	syntax.addFlag(kSourcedFlag, kSourcedFlagLong, MSyntax::kString);
	syntax.addFlag(kTargetFlag, kTargetFlagLong, MSyntax::kString);
	syntax.addFlag(kJointsFlag, kJointsFlagLong, MSyntax::kString);
	syntax.addFlag(kStartFrameFlag,	kStartFrameFlagLong, MSyntax::kLong);
	syntax.addFlag(kEndFrameFlag, kEndFrameFlagLong, MSyntax::kLong);
	syntax.addFlag(kNumBonesFlag, kNumBonesFlagLong, MSyntax::kLong);
	syntax.addFlag(kPatienceFlag, kPatienceFlagLong, MSyntax::kLong);
	syntax.addFlag(kToleranceFlag, kToleranceFlagLong, MSyntax::kDouble);
	syntax.addFlag(kReuseSkeletonFlag, kReuseSkeletonFlagLong, MSyntax::kBoolean);

	syntax.makeFlagMultiUse(kJointsFlag);

	syntax.enableQuery(false);
	syntax.enableEdit(false);

	return syntax;
}

void* DemBonesCmd::creator()
{
	return new DemBonesCmd();
}

bool DemBonesCmd::isUndoable() const
{
	return false;
}

MStatus DemBonesCmd::doIt(const MArgList& args)
{
	MStatus status;
	MArgDatabase argData(syntax(), args);

	if (!argData.isFlagSet(kSourcedFlag))
	{
		MGlobal::displayError("Missing argument 'sourceMesh'");
		return MS::kFailure;
	}

	if (!argData.isFlagSet(kTargetFlag))
	{
		MGlobal::displayError("Missing argument 'targetMesh'");
		return MS::kFailure;
	}

	if (!argData.isFlagSet(kStartFrameFlag))
	{
		MGlobal::displayError("Missing argument 'startFrame'");
		return MS::kFailure;
	}

	if (!argData.isFlagSet(kEndFrameFlag))
	{
		MGlobal::displayError("Missing argument 'endFrame'");
		return MS::kFailure;
	}

	if (!argData.isFlagSet(kNumBonesFlag))
	{
		MGlobal::displayError("Missing argument 'numBones'");
		return MS::kFailure;
	}

	MString sourceMeshName;
	MString targetMeshName;

	status = argData.getFlagArgument(kSourcedFlag, 0, sourceMeshName);
	CHECK_MSTATUS_AND_RETURN_IT(status);
	status = argData.getFlagArgument(kTargetFlag, 0, targetMeshName);
	CHECK_MSTATUS_AND_RETURN_IT(status);
	
	m_globalItersSet = argData.isFlagSet(kGlobalItersFlag);
	if (m_globalItersSet)
	{
		status = argData.getFlagArgument(kGlobalItersFlag, 0, m_globalIters);
		CHECK_MSTATUS_AND_RETURN_IT(status);
	}

	m_weightItersSet = argData.isFlagSet(kWeightsItersFlag);
	if (m_weightItersSet)
	{
		status = argData.getFlagArgument(kWeightsItersFlag, 0, m_weightIters);
		CHECK_MSTATUS_AND_RETURN_IT(status);
	}


	m_transItersSet = argData.isFlagSet(kTransItersFlag);
	if (m_transItersSet)
	{
		status = argData.getFlagArgument(kTransItersFlag, 0, m_transIters);
		CHECK_MSTATUS_AND_RETURN_IT(status);
	}

	m_patienceSet = argData.isFlagSet(kPatienceFlag);
	if (m_patienceSet)
	{
		status = argData.getFlagArgument(kPatienceFlag, 0, m_patience);
		CHECK_MSTATUS_AND_RETURN_IT(status);
	}

	m_toleranceSet = argData.isFlagSet(kToleranceFlag);
	if (m_toleranceSet)
	{
		status = argData.getFlagArgument(kToleranceFlag, 0, m_tolerance);
		CHECK_MSTATUS_AND_RETURN_IT(status);
	}

	m_reuseSkeletonSet = argData.isFlagSet(kReuseSkeletonFlag);
	if (m_reuseSkeletonSet)
	{
		status = argData.getFlagArgument(kReuseSkeletonFlag, 0, m_reuseSkeleton);
		CHECK_MSTATUS_AND_RETURN_IT(status);
	}

	status = argData.getFlagArgument(kStartFrameFlag, 0, m_startFrame);
	CHECK_MSTATUS_AND_RETURN_IT(status);

	status = argData.getFlagArgument(kEndFrameFlag, 0, m_endFrame);
	CHECK_MSTATUS_AND_RETURN_IT(status);

	status = argData.getFlagArgument(kNumBonesFlag, 0, m_numBones);
	CHECK_MSTATUS_AND_RETURN_IT(status);

	// Store ExampleMesh and Joints as MDagPath
	status = MayaUtils::getDagPathFromName(sourceMeshName, m_sourceMesh);
	CHECK_MSTATUS_AND_RETURN_IT(status);

	status = MayaUtils::getDagPathFromName(targetMeshName, m_targetMesh);
	CHECK_MSTATUS_AND_RETURN_IT(status);

	m_joints.setLength(m_jointNames.length());
	for (unsigned int ii=0; ii<m_jointNames.length(); ++ii)
	{
		status = MayaUtils::getDagPathFromName(m_jointNames[ii], m_joints[ii]);
		CHECK_MSTATUS_AND_RETURN_IT(status);
	}

	return redoIt();
}

MStatus DemBonesCmd::redoIt()
{
	MStatus status;
	try
	{
		status = solveWeights();
	}
	catch (std::exception &e)
	{
		std::cout << "Unexpected exception\n" << e.what() << "\n";
		status = MS::kFailure;
	}

	return status;
}

MStatus DemBonesCmd::solveWeights()
{
	MStatus status;
	MTime time;
	
	DemBonesCustom demBones;

	// startFrame is supposed to contain the bind pose
	time.setValue(m_startFrame);
	MAnimControl::setCurrentTime(time);

	Eigen::MatrixXd u;
	std::vector<std::vector<int>> fv;

	demBones.clear();

	if (m_globalItersSet)
		demBones.nIters = m_globalIters;
	if (m_transItersSet)
		demBones.nTransIters = m_transIters;
	if (m_weightItersSet)
		demBones.nWeightsIters = m_weightIters;
	if (m_patienceSet)
		demBones.m_patience = m_patience;
	if (m_toleranceSet)
		demBones.m_tolerance = m_tolerance;
	// I guess the rest of the parameters are default

	MFnMesh fnMesh(m_sourceMesh);

	int nV = fnMesh.numVertices();
	MPointArray vertices;
	fnMesh.getPoints(vertices, MSpace::kWorld);
	u.resize(3, nV);
	for (int ii = 0; ii < nV; ++ii)
	{
		u.col(ii) << vertices[ii].x, vertices[ii].y, vertices[ii].z;
	}
	
	fv.resize(fnMesh.numPolygons());
	for (int ii = 0; ii < fv.size(); ++ii)
	{
		MIntArray polygonVertices;
		fnMesh.getPolygonVertices(ii, polygonVertices);
		fv[ii].resize(polygonVertices.length());
		for (unsigned int jj = 0; jj < polygonVertices.length(); ++jj)
		{
			fv[ii][jj] = polygonVertices[jj];
		}
	}

	// Number of subjects. It seems to be 1??
	demBones.nS = 1;
	// Vertices in rest pose
	demBones.u = u;
	// Topology structure
	demBones.fv = fv;
	// Number of vertices
	demBones.nV = nV;
	// Number of frames
	demBones.nF = m_endFrame - m_startFrame + 1;

	// Resize v to store mesh vertex positions for all the sequence
	demBones.v.resize(3 * demBones.nF, demBones.nV);
	demBones.fTime.resize(demBones.nF);
	// fStart stores an offset just if multiple subjecst were used. Anyway, its necessary to have always nS + 1 because its used
	// inside the library in some computations
	demBones.fStart.resize(demBones.nS + 1);
	demBones.fStart(0) = 0;
	demBones.fStart(1) = demBones.nF;

	std::cout << "Reading " << demBones.nF << " frames ";
	// Loop all the keyframes and store mesh sequence
	int fTime{ 0 };
	for (int ii = m_startFrame; ii <= m_endFrame; ++ii)
	{
		// Set Maya time
		time.setValue(ii);
		MAnimControl::setCurrentTime(time);
		MTime time = MAnimControl::currentTime();
		std::cout << ".";

		demBones.fTime(fTime) = fTime;
		// Store mesh vertices position for this pose
		MPointArray vertices;
		fnMesh.getPoints(vertices, MSpace::kWorld);
		for (int jj = 0; jj < demBones.nV; ++jj)
		{
			demBones.v.col(jj).segment<3>(fTime * 3) << vertices[jj].x, vertices[jj].y, vertices[jj].z;
		}
		fTime++;
	}
	std::cout << "\n";
	// This structure stores the subject that should be use for a specific time
	demBones.subjectID.resize(demBones.nF);
	for (int ii = 0; ii < demBones.nF; ++ii)
	{
		demBones.subjectID(ii) = 0;
	}

	// targetMesh has to point to the shape to getSkinCluster correctly
	MDagPath targetMeshShape = m_targetMesh;
	MayaUtils::extendToShapeWithType(targetMeshShape, MFn::kMesh);
	m_skinData.setDagPath(targetMeshShape);

	MObject skinCluster;
	MayaUtils::getSkinCluster(targetMeshShape, skinCluster);

	bool needCreateJoints = demBones.boneName.size() == 0;
	bool hasExistingSkeleton = !skinCluster.isNull();
	
	// Check if we should reuse existing skeleton
	if (m_reuseSkeleton && hasExistingSkeleton)
	{
		std::cout << "Reusing existing skeleton...\n";
		
		MFnSkinCluster fnSkin(skinCluster, &status);
		CHECK_MSTATUS_AND_RETURN_IT(status);
		
		MDagPathArray influenceDagPaths;
		fnSkin.influenceObjects(influenceDagPaths);
		
		// Get existing joints
		m_joints.clear();
		m_joints.setLength(influenceDagPaths.length());
		demBones.boneName.resize(influenceDagPaths.length());
		
		for (unsigned int i = 0; i < influenceDagPaths.length(); ++i)
		{
			m_joints[i] = influenceDagPaths[i];
			demBones.boneName[i] = influenceDagPaths[i].partialPathName().asUTF8();
		}
		
		// Update demBones with existing skeleton info
		demBones.nB = influenceDagPaths.length();
		demBones.bind.resize(demBones.nS * 4, demBones.nB * 4);
		
		// Get bind matrices from existing skeleton
		time.setValue(m_startFrame);
		MAnimControl::setCurrentTime(time);
		
		for (unsigned int i = 0; i < m_joints.length(); ++i)
		{
			MDagPath &boneDagPath = m_joints[i];
			MFnDagNode fnDagNode(boneDagPath);
			MObject worldMatrixAttr = fnDagNode.attribute("worldMatrix");
			MPlug worldMatrixPlug(boneDagPath.node(), worldMatrixAttr);
			worldMatrixPlug.selectAncestorLogicalIndex(0, worldMatrixAttr);
			
			MObject worldMatrixOb;
			worldMatrixPlug.getValue(worldMatrixOb);
			MFnMatrixData worldMatrixData(worldMatrixOb);
			MMatrix worldMatrix = worldMatrixData.matrix();
			
			demBones.bind.blk4(0, i) = Eigen::Map<Eigen::Matrix4d>((double*)worldMatrix.matrix);
		}
		
		// Setup parent structure
		demBones.parent.resize(demBones.nB);
		for (unsigned int i = 0; i < m_joints.length(); ++i)
		{
			MDagPath parentPath = m_joints[i];
			parentPath.pop();
			
			demBones.parent[i] = -1;
			for (unsigned int j = 0; j < m_joints.length(); ++j)
			{
				if (m_joints[j].node() == parentPath.node())
				{
					demBones.parent[i] = j;
					break;
				}
			}
		}
		
		// Compute with existing skeleton - only update weights
		std::cout << "Computing weights for existing skeleton...\n";
		demBones.computeWeights();
		
		needCreateJoints = false;
	}
	else if (needCreateJoints)
	{
		demBones.boneName.resize(demBones.nB);
		for (int b = 0; b < demBones.nB; ++b)
		{
			std::ostringstream ss;
			ss << kDefaultJointName << b;
			demBones.boneName[b] = ss.str();
		}
	}
	
	// Only create new joints if needed
	if (needCreateJoints)
	{
		Eigen::MatrixXd lr, lt, gb, lbr, lbt;
		demBones.computeRTB(0, lr, lt, gb, lbr, lbt);
		
		MDagPath rootJointDagPath;
		MObject rootJoint;
		MayaUtils::createJoint("joint_root", rootJoint);
		MDagPath::getAPathTo(rootJoint, rootJointDagPath);
		m_joints.clear();
		// Create the joints and animate them
		createJoints(demBones, rootJointDagPath, m_joints);
		
		MTime time;
		time.setValue(m_startFrame);
		MAnimControl::setCurrentTime(time);

		// Set the bones in initial position
		unsigned int numBones = demBones.boneName.size();
		for (unsigned int b = 0; b < numBones; ++b)
		{
			MDagPath joint = m_joints[b];
			MayaUtils::setPosition(joint.node(), MPoint(lbt(0, b), lbt(1, b), lbt(2, b)), MSpace::kTransform);
			MEulerRotation rot = MEulerRotation(lbr(0, b), lbr(1, b), lbr(2, b));
			MayaUtils::setRotation(joint.node(),  rot, MSpace::kTransform);
		}

		// Create animation curves
		for (unsigned int b = 0; b < numBones; ++b)
		{
			MObject joint = m_joints[b].node();
			MFnDependencyNode fnDep(joint, &status);
			MPlug txPlug = fnDep.findPlug("tx");
			MPlug tyPlug = fnDep.findPlug("ty");
			MPlug tzPlug = fnDep.findPlug("tz");
			MPlug rxPlug = fnDep.findPlug("rx");
			MPlug ryPlug = fnDep.findPlug("ry");
			MPlug rzPlug = fnDep.findPlug("rz");

			MFnAnimCurve fnAnimTx, fnAnimTy, fnAnimTz, fnAnimRx, fnAnimRy, fnAnimRz;
			MObject txCurve = fnAnimTx.create(txPlug, MFnAnimCurve::AnimCurveType::kAnimCurveTL);
			MObject tyCurve = fnAnimTy.create(tyPlug, MFnAnimCurve::AnimCurveType::kAnimCurveTL);
			MObject tzCurve = fnAnimTz.create(tzPlug, MFnAnimCurve::AnimCurveType::kAnimCurveTL);
			MObject rxCurve = fnAnimRx.create(rxPlug, MFnAnimCurve::AnimCurveType::kAnimCurveTL);
			MObject ryCurve = fnAnimRy.create(ryPlug, MFnAnimCurve::AnimCurveType::kAnimCurveTL);
			MObject rzCurve = fnAnimRz.create(rzPlug, MFnAnimCurve::AnimCurveType::kAnimCurveTL);

			Eigen::VectorXd translation = lt.col(b);
			Eigen::VectorXd rotation = lr.col(b);
			Eigen::VectorXd tx = Eigen::Map<Eigen::VectorXd, 0, Eigen::InnerStride<3>>(translation.data(), translation.size() / 3);
			Eigen::VectorXd ty = Eigen::Map<Eigen::VectorXd, 0, Eigen::InnerStride<3>>(translation.data()+1, translation.size() / 3);
			Eigen::VectorXd tz = Eigen::Map<Eigen::VectorXd, 0, Eigen::InnerStride<3>>(translation.data()+2, translation.size() / 3);

			Eigen::VectorXd rx = Eigen::Map<Eigen::VectorXd, 0, Eigen::InnerStride<3>>(rotation.data(), rotation.size() / 3);
			Eigen::VectorXd ry = Eigen::Map<Eigen::VectorXd, 0, Eigen::InnerStride<3>>(rotation.data() + 1, rotation.size() / 3);
			Eigen::VectorXd rz = Eigen::Map<Eigen::VectorXd, 0, Eigen::InnerStride<3>>(rotation.data() + 2, rotation.size() / 3);
			unsigned int idx = 0;
			for (int f = m_startFrame; f <= m_endFrame; ++f)
			{
				time.setValue(f);
				fnAnimTx.addKeyframe(time, tx(idx));
				fnAnimTy.addKeyframe(time, ty(idx));
				fnAnimTz.addKeyframe(time, tz(idx));
				fnAnimRx.addKeyframe(time, rx(idx));
				fnAnimRy.addKeyframe(time, ry(idx));
				fnAnimRz.addKeyframe(time, rz(idx));
				++idx;
			}
		}
	}

	// If there is no skinCluster we are going to generate one
	if (skinCluster.isNull())
	{
		MDGModifier dgMod;
		// Set startFrame in order to have bind matrices correct when applying skinCluster
		time.setValue(m_startFrame);
		MAnimControl::setCurrentTime(time);

		std::stringstream cmd;
		cmd << "skinCluster -toSelectedBones ";
		for (unsigned int ii=0; ii<m_joints.length(); ++ii)
		{
			cmd << m_joints[ii].partialPathName().asUTF8() << " ";
		}
		cmd << m_targetMesh.partialPathName().asUTF8();

		status = dgMod.commandToExecute(cmd.str().c_str());
		CHECK_MSTATUS_AND_RETURN_IT(status);

		status = dgMod.doIt();
		CHECK_MSTATUS_AND_RETURN_IT(status);
	}

	MayaUtils::getSkinCluster(targetMeshShape, skinCluster);
	MFnSkinCluster fnSkin(skinCluster, &status);
	CHECK_MSTATUS_AND_RETURN_IT(status);

	MDagPathArray influenceDagPaths;
	fnSkin.influenceObjects(influenceDagPaths);

	for (unsigned int ii = 0; ii < influenceDagPaths.length(); ++ii)
	{
		std::string influenceName = influenceDagPaths[ii].partialPathName().asUTF8();
	}

	int numVertices = demBones.w.outerSize();
	int numBones = demBones.w.innerSize();

	// Loop through vertices
	for (int c = 0; c < numVertices; ++c)
	{
		// Loop through bones
		MIntArray influenceIndices;
		MDoubleArray weights;
		//std::string message = "Vertex " + std::to_string(c) + ": ";
		for (Eigen::SparseMatrix<double>::InnerIterator it(demBones.w, c); it; ++it)
		{
			int influenceIdx = it.row();
			double weight = it.value();

			influenceIndices.append(influenceIdx);
			weights.append(weight);
			//message += std::to_string(influenceIdx) + ": " + std::to_string(weight) + ", ";
		}
		//std::cout << message << std::endl;
		MayaUtils::setVertexInfluenceWeights(fnSkin, targetMeshShape, c, influenceIndices, weights, false);
	}
	return status;
}

MStatus DemBonesCmd::solveTransformsAndWeights()
{
	return MStatus();
}

MStatus DemBonesCmd::createJoints(DemBonesCustom & demBones, const MDagPath &parent, MDagPathArray &joints)
{
	MObject root;
	/// Create root bones
	unsigned int numBones = demBones.boneName.size();
	joints.setLength(numBones);
	for (unsigned int b = 0; b < numBones; ++b)
	{
		if (demBones.parent[b] == -1)
		{
			MObject newJoint;
			if (parent.isValid())
				MayaUtils::createJoint(MString(demBones.boneName[b].c_str()), parent.node(), newJoint);
			else
				MayaUtils::createJoint(MString(demBones.boneName[b].c_str()), newJoint);

			MDagPath::getAPathTo(newJoint, joints[b]);
			root = newJoint;
		}
	}

	for (unsigned int b = 0; b < numBones; ++b)
	{
		if (demBones.parent[b] != -1)
		{
			MObject newJoint;
			MayaUtils::createJoint(MString(demBones.boneName[b].c_str()), newJoint);
			MDagPath::getAPathTo(newJoint, joints[b]);
			MDagPath &parent = joints[demBones.parent[b]];
			if (parent.isValid())
				MayaUtils::setParent(joints[b], parent);
		}
	}
	return MS::kSuccess;
}



