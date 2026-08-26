#ifndef __MAYA_DAG_UTILS_H__
#define __MAYA_DAG_UTILS_H__

#include <maya/MString.h>
#include <maya/MFn.h>
#include <maya/MStringArray.h>
#include <maya/MObjectArray.h>

namespace MayaUtils
{
	MStatus getDagPathFromName(const MString &name, MDagPath &dagPath);
	/**
	 * Its super common to have a Transform node and want the Shape below. Normally we use MDagPath::extendToShape. This function 
	 * performs the same operation checking that the shape is an specific type
	 */
	MStatus extendToShapeWithType(MDagPath &dagPath, MFn::Type type);

	MStatus setMatrix(const MObject &ob, const MMatrix &matrix);

	MStatus setPosition(const MObject &ob, const MPoint &pos, MSpace::Space space);

	MStatus setRotation(const MObject &ob, const MQuaternion &rot, MSpace::Space space);

	MStatus setRotation(const MObject &ob, const MEulerRotation &rot, MSpace::Space space);

	MStatus setScale(const MObject &ob, const MPoint &sca, MSpace::Space space);

	MStatus setParent(MObject &child, MObject &parent);

	MStatus setParent(MDagPath &child, MDagPath &parent);
}

#endif