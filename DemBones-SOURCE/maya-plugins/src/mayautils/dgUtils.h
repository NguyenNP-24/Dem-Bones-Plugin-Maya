#ifndef __MAYA_DG_UTILS_H__
#define __MAYA_DG_UTILS_H__

#include <maya/MStatus.h>
#include <maya/MObject.h>
#include <maya/MDagPath.h>
#include <maya/MPlug.h>
#include <maya/MFnDependencyNode.h>

namespace MayaUtils
{
	bool existsPlug(const MObject &ob, const MString &plugName);

	bool isPlugConnected(const MObject& mObject, const MObject& mPlug);

	MStatus connectPlugs(const MObject &obSrc, const MObject &obDst, const MString &plugSrcName, const MString &plugDstName);

	MStatus connectPlugs(const MFnDependencyNode &fnDepNodeSrc, const MFnDependencyNode &fnDepNodeDst, const MString &plugSrcName, const MString &plugDstName);


	template <typename T>
	T getPlugValue(const MDagPath& mDagPath, const MObject& mPlug, const T defaultValue)
	{
		MStatus status;
		const MObject mObject = mDagPath.node(&status);
		if (status)
		{
			MPlug plug(mObject, mPlug);
			if (!plug.isNull())
			{
				T value;
				if (plug.getValue(value))
				{
					return value;
				}
			}
		}
		return defaultValue;
	}

	template <typename T>
	T getPlugValue(const MObject &ob, const MString &plugName, const T &defaultValue)
	{
		MStatus status;
		MFnDependencyNode fnDep(ob, &status);
		if (status)
		{
			MPlug plug = fnDep.findPlug(plugName);
			if (!plug.isNull())
			{
				T value;
				if (plug.getValue(value))
				{
					return value;
				}
			}
		}
		return defaultValue;
	}

	template <typename T>
	MStatus setPlugValue(const MObject &ob, const MString &plugName, const T &value)
	{
		MStatus status;
		MFnDependencyNode fnDep(ob, &status);
		if (status)
		{
			MPlug plug = fnDep.findPlug(plugName);
			if (!plug.isNull())
			{
				plug.setValue(value);
			}
		}
		return status;
	}
}

#endif