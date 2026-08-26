#include "dgUtils.h"

#include <maya/MFnDependencyNode.h>
#include <maya/MPlug.h>
#include <maya/MDGModifier.h>


namespace MayaUtils
{
	MStatus connectPlugs(const MObject & obSrc, const MObject & obDst, const MString & plugSrcName, const MString & plugDstName)
	{
		MStatus status;
		MDGModifier dgMod;
		MFnDependencyNode fnDepNodeSrc;
		MFnDependencyNode fnDepNodeDst;
		status = fnDepNodeSrc.setObject(obSrc);
		CHECK_MSTATUS_AND_RETURN_IT(status);
		status = fnDepNodeDst.setObject(obDst);
		CHECK_MSTATUS_AND_RETURN_IT(status);
		MPlug plugSrc = fnDepNodeSrc.findPlug(plugSrcName, true, &status);
		CHECK_MSTATUS_AND_RETURN_IT(status);
		MPlug plugDst = fnDepNodeDst.findPlug(plugDstName, true, &status);
		CHECK_MSTATUS_AND_RETURN_IT(status);
		status = dgMod.connect(plugSrc, plugDst);
		CHECK_MSTATUS_AND_RETURN_IT(status);
		return dgMod.doIt();
	}

	MStatus connectPlugs(const MFnDependencyNode & fnDepNodeSrc, const MFnDependencyNode & fnDepNodeDst, const MString & plugSrcName, const MString & plugDstName)
	{
		MStatus status;
		MDGModifier dgMod;
		MPlug plugSrc = fnDepNodeSrc.findPlug(plugSrcName, status);
		CHECK_MSTATUS_AND_RETURN_IT(status);
		MPlug plugDst = fnDepNodeDst.findPlug(plugDstName, status);
		CHECK_MSTATUS_AND_RETURN_IT(status);
		status = dgMod.connect(plugSrc, plugDst);
		CHECK_MSTATUS_AND_RETURN_IT(status);
		return dgMod.doIt();
	}

	bool existsPlug(const MObject & ob, const MString & plugName)
	{
		bool result{ false };
		MStatus status;
		MFnDependencyNode fnDepNode(ob, &status);
		CHECK_MSTATUS(status);
		if (status == MS::kSuccess)
		{
			MPlug plug = fnDepNode.findPlug(plugName);
			result = !plug.isNull();
		}
		return result;
	}

	bool isPlugConnected(const MObject & mObject, const MObject & mPlug)
	{
		MPlug plug(mObject, mPlug);
		return plug.isConnected();
	}
}