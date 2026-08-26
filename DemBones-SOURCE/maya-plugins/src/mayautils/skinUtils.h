#ifndef __MAYA_SKIN_UTILS_H__
#define __MAYA_SKIN_UTILS_H__

#include <maya/MGlobal.h>
#include <maya/MDagPath.h>
#include <maya/MFnSkinCluster.h>
#include <maya/MFnSingleIndexedComponent.h>
#include <maya/MItDependencyGraph.h>
#include <maya/MIntArray.h>
#include <maya/MDoubleArray.h>

namespace MayaUtils
{
	MStatus createJoint(const MString & name, MObject &joint);

	MStatus createJoint(const MString &name, const MObject &parent, MObject &joint);

	MStatus getSkinCluster(const MDagPath& dagPath, MObject& skinCluster);

	MStatus getInfluenceObjects(const MObject& skinCluster, MDagPathArray& dagPathArray);

	MStatus setVertexInfluenceWeights(MFnSkinCluster &fnSkin, const MDagPath &dagPath, int vertexIndex, MIntArray &influences, MDoubleArray &weights, bool normalize = false);
}

#endif