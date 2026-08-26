#include "dagUtils.h"

#include <maya/MDagPath.h>
#include <maya/MDagPathArray.h>
#include <maya/MObject.h>
#include <maya/MObjectArray.h>
#include <maya/MSelectionList.h>
#include <maya/MItDag.h>

#include <maya/MVector.h>
#include <maya/MQuaternion.h>
#include <maya/MEulerRotation.h>

#include <maya/MFnDagNode.h>
#include <maya/MFnTransform.h>

#include <string>

namespace MayaUtils
{	
	MStatus getDagPathFromName(const MString & name, MDagPath & dagPath)
	{
		MSelectionList list;
		MStatus status = list.add(name);
		CHECK_MSTATUS_AND_RETURN_IT(status);
		status = list.getDagPath(0, dagPath);
		return status;
	}

	MStatus extendToShapeWithType(MDagPath& path, MFn::Type type)
	{
		MStatus status;
		if (path.apiType() == type)
		{
			return MS::kSuccess;
		}
		unsigned int shapeCount;
		status = path.numberOfShapesDirectlyBelow(shapeCount);
		for (unsigned int ii = 0; ii < shapeCount; ++ii)
		{
			status = path.extendToShapeDirectlyBelow(ii);
			CHECK_MSTATUS_AND_RETURN_IT(status);
			if (path.hasFn(type))
			{
				MFnDagNode fnNode(path, &status);
				CHECK_MSTATUS_AND_RETURN_IT(status);
				if (!fnNode.isIntermediateObject())
				{
					return MS::kSuccess;
				}
			}
			path.pop();
		}
		return MS::kFailure;
	}
	MStatus setMatrix(const MObject & ob, const MMatrix & matrix)
	{
		MStatus status;
		MFnTransform fnTransform(ob, &status);
		CHECK_MSTATUS_AND_RETURN_IT(status);
		MTransformationMatrix xmatrix(matrix);
		status = fnTransform.set(xmatrix);
		CHECK_MSTATUS_AND_RETURN_IT(status);
		return MS::kSuccess;
	}

	MStatus setPosition(const MObject & ob, const MPoint & pos, MSpace::Space space)
	{
		MStatus status;
		MFnTransform fnTransform(ob, &status);
		CHECK_MSTATUS_AND_RETURN_IT(status);
		status = fnTransform.setTranslation(MVector(pos), space);
		CHECK_MSTATUS_AND_RETURN_IT(status);
		return MS::kSuccess;
	}

	MStatus setRotation(const MObject & ob, const MQuaternion & rot, MSpace::Space space)
	{
		MStatus status;
		MFnTransform fnTransform(ob, &status);
		CHECK_MSTATUS_AND_RETURN_IT(status);
		status = fnTransform.setRotation(rot, space);
		CHECK_MSTATUS_AND_RETURN_IT(status);
		return MS::kSuccess;
	}

	MStatus setRotation(const MObject & ob, const MEulerRotation & rot, MSpace::Space space)
	{
		return setRotation(ob, rot.asQuaternion(), space);
	}

	MStatus setScale(const MObject & ob, const MPoint & sca, MSpace::Space space)
	{
		MStatus status;
		MFnTransform fnTransform(ob, &status);
		CHECK_MSTATUS_AND_RETURN_IT(status);
		double scale[3] = { sca.x, sca.y, sca.z };
		status = fnTransform.setScale(scale);
		CHECK_MSTATUS_AND_RETURN_IT(status);

		return MS::kSuccess;
	}
	MStatus setParent(MObject & child, MObject & parent)
	{
		MStatus status;
		MFnDagNode fnDag(parent, &status);
		CHECK_MSTATUS_AND_RETURN_IT(status);

		return fnDag.addChild(child);
	}

	MStatus setParent(MDagPath & child, MDagPath & parent)
	{
		MStatus status;
		MFnDagNode fnDag(parent, &status);
		CHECK_MSTATUS_AND_RETURN_IT(status);

		return fnDag.addChild(child.node());
	}
}

