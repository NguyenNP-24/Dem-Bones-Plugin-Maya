#include "skinUtils.h"

#include <maya/MFnDagNode.h>
#include <maya/MDGModifier.h>
#include <maya/MDagModifier.h>

namespace MayaUtils
{
	MStatus createJoint(const MString & name, MObject &joint)
	{
		MStatus status;
		MDagModifier dagMod;
		joint = dagMod.createNode("joint");
		CHECK_MSTATUS_AND_RETURN_IT(status);
		status = dagMod.renameNode(joint, name);
		CHECK_MSTATUS_AND_RETURN_IT(status);
		status = dagMod.doIt();
		CHECK_MSTATUS_AND_RETURN_IT(status);
		return status;
	}

	MStatus createJoint(const MString &name, const MObject &parent, MObject &joint)
	{
		MStatus status;
		MDagModifier dagMod;
		joint = dagMod.createNode("joint", parent, &status);
		CHECK_MSTATUS_AND_RETURN_IT(status);
		status = dagMod.renameNode(joint, name);
		CHECK_MSTATUS_AND_RETURN_IT(status);
		status = dagMod.doIt();
		CHECK_MSTATUS_AND_RETURN_IT(status);
	}

	MStatus getSkinCluster(const MDagPath& dagPath, MObject& skinCluster)
	{
		MObject node = dagPath.node();
		MItDependencyGraph it = MItDependencyGraph(node, MFn::kSkinClusterFilter, MItDependencyGraph::kUpstream);
		if (!it.isDone())
		{
			skinCluster = it.currentItem();
			return MS::kSuccess;
		}
		skinCluster = MObject::kNullObj;
		return MS::kFailure;
	}

	MStatus getInfluenceObjects(const MObject& skinCluster, MDagPathArray& dagPathArray)
	{
		MStatus status;
		MFnSkinCluster fnSkin(skinCluster, &status);
		fnSkin.influenceObjects(dagPathArray, &status);
		return status;
	}

	MStatus setVertexInfluenceWeights(MFnSkinCluster &fnSkin, const MDagPath& dagPath, int vertexIndex, MIntArray& influences, MDoubleArray& weights, bool normalize)
	{
		MStatus status;
		MFnSingleIndexedComponent fnComp;
		MObject component = fnComp.create(MFn::kMeshVertComponent, &status);
		CHECK_MSTATUS_AND_RETURN_IT(status);
		status = fnComp.addElement(vertexIndex);
		CHECK_MSTATUS_AND_RETURN_IT(status);
		status = fnSkin.setWeights(dagPath, component, influences, weights, normalize);
		CHECK_MSTATUS_AND_RETURN_IT(status);
		return status;
	}

}