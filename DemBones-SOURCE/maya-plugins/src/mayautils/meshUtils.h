#ifndef _meshUtils
#define _meshUtils

#include <maya/MGlobal.h>
#include <maya/MFnMesh.h>
#include <maya/MFnDagNode.h>

#include <maya/MDagPath.h>
#include <maya/MObject.h>
#include <maya/MMatrix.h>
#include <maya/MPoint.h>
#include <maya/MPointArray.h>
#include <maya/MVector.h>
#include <maya/MFloatPointArray.h>
#include <maya/MBoundingBox.h>


inline MStatus getShapeNode(MDagPath& path)
{
	MStatus status;
	if (path.apiType() == MFn::kMesh)
	{
		return MS::kSuccess;
	}
	unsigned int shapeCount;
	status = path.numberOfShapesDirectlyBelow(shapeCount);
	for (unsigned int ii=0; ii<shapeCount; ++ii) {
		status = path.extendToShapeDirectlyBelow(ii);
		CHECK_MSTATUS_AND_RETURN_IT(status);
		if (path.hasFn(MFn::kMesh)) {
			MFnDagNode fnNode(path, &status);
			CHECK_MSTATUS_AND_RETURN_IT(status);
			if (!fnNode.isIntermediateObject()) {
				return MS::kSuccess;
			}
		}
		path.pop();
	}
	return MS::kFailure;
}

inline void ExpandBB(MBoundingBox& bb, const MPointArray& meshPoints)
{
	for (unsigned int ii=0; ii<meshPoints.length(); ++ii) {
		bb.expand(meshPoints[ii]);
	}
}

inline float squareDistPointAABB(const MPoint& point, const MBoundingBox& aabb)
{
	double squareDist = 0.0f;
	MPoint min = aabb.min();
	MPoint max = aabb.max();
	if (point.x < min.x) squareDist += (min.x - point.x) * (min.x - point.x);
	if (point.x > max.x) squareDist += (point.x - max.x) * (point.x - max.x);
	if (point.y < min.y) squareDist += (min.y - point.y) * (min.y - point.y);
	if (point.y > max.y) squareDist += (point.y - max.y) * (point.y - max.y);
	if (point.z < min.z) squareDist += (min.z - point.z) * (min.z - point.z);
	if (point.z > max.z) squareDist += (point.z - max.z) * (point.z - max.z);
	return squareDist;
}

inline bool IsPointInsideMesh(const MPoint& point, MFnMesh& fnMesh, MFloatPointArray& hitPoints,const MVector& rayDir=MVector(0,1,0))
{
	MStatus status;
	hitPoints.clear();

	fnMesh.allIntersections(point, rayDir, NULL, NULL,
		false, MSpace::kWorld, 10000, false, NULL, false, 
		hitPoints, NULL, NULL, NULL, NULL, NULL, 9.999999975e-007F, &status);
	if (status != MS::kSuccess) {
		MGlobal::displayError("Error meshUtils.IsPointInsideMesh");
		return false;
	}
	return hitPoints.length() % 2 == 1;
}


#endif