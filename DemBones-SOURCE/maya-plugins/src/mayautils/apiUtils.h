
#ifndef _apiUtils_h
#define _apiUtils_h

#include <string>
#include <algorithm>

using namespace std;

#include <maya/MGlobal.h>
#include <maya/MObject.h>
#include <maya/MPlug.h>
#include <maya/M3dView.h>
#include <maya/MDagPath.h>
#include <maya/MSelectionList.h>
#include <maya/MPoint.h>
#include <maya/MVector.h>
#include <maya/MMatrix.h>
#include <maya/MEulerRotation.h>
#include <maya/MArrayDataHandle.h>
#include <maya/MArrayDataBuilder.h>

inline MStatus GetRGBFromPlug(const MObject& ob, const MObject& attr, float& r, float& g, float& b)
{
	MPlug plugColor(ob, attr);
	plugColor.child(0).getValue(r);
	plugColor.child(1).getValue(g);
	plugColor.child(2).getValue(b);

	return MS::kSuccess;
}

inline MStatus GetDagPathFromMObject(const MObject& ob, MDagPath& dagPath)
{
	MStatus status;
	MSelectionList selectionList;
	status = selectionList.add(ob);
	status = selectionList.getDagPath(0, dagPath);
	return status;
}

inline MStatus GetCameraMatrixFromView3D(M3dView& view3d, MMatrix& cameraMatrix)
{
	MStatus status;
	MDagPath cameraPath;
	status = view3d.getCamera(cameraPath);
	cameraMatrix = cameraPath.inclusiveMatrix();
	return status;
}

inline float GetDistanceFromCamera(const MMatrix& matrix, M3dView& view)
{
	MVector position(matrix[3][0], matrix[3][1], matrix[3][2]);
	MMatrix camMatrix;
	GetCameraMatrixFromView3D(view, camMatrix);
	MVector camPos(camMatrix[3][0], camMatrix[3][1], camMatrix[3][2]);
	// Return the Length
	return (float)((position - camPos).length());
}

inline float GetClampedLerp(const float& a, const float& b, const float& t, const float& min, const float& max)
{
	float clamp = std::min(1.0f, std::max(0.0f, (t - min) / (max - min)));
	return (a + (b - a) * clamp);
}

inline void PrintInfo(string message)
{
	MGlobal::displayInfo(MString(message.c_str()));
}

inline void PrintWarning(string message)
{
	MGlobal::displayWarning(MString(message.c_str()));
}

inline void PrintMPoint(string header, const MPoint& mPoint)
{
	string message = header;
	message += "(" + to_string(mPoint.x) + "," + to_string(mPoint.y) + "," + to_string(mPoint.z) + ")";
	MGlobal::displayInfo(MString(message.c_str()));
}

inline void PrintMVector(string header, const MVector &mVec)
{
	string message = header;
	message += "(" + to_string(mVec.x) + "," + to_string(mVec.y) + "," + to_string(mVec.z) + ")";
	MGlobal::displayInfo(MString(message.c_str()));
}

inline void PrintMEulerRotation(string header, const MEulerRotation &mEuler)
{
	string message = header;
	message += "(" + to_string(mEuler.x) + "," + to_string(mEuler.y) + "," + to_string(mEuler.z) + ")";
	MGlobal::displayInfo(MString(message.c_str()));
}

inline void PrintMMatrix(string header, const MMatrix &mMatrix)
{
	string message = header + " [\n";
	message += "[[" + to_string(mMatrix[0][0]) + "],[" + to_string(mMatrix[0][1]) + "],[" + to_string(mMatrix[0][2]) + "] " + "],[" + to_string(mMatrix[0][3]) + "]\n";
	message += "[" + to_string(mMatrix[1][0]) + "],[" + to_string(mMatrix[1][1]) + "],[" + to_string(mMatrix[1][2]) + "] " + "],[" + to_string(mMatrix[1][3]) + "]\n";
	message += "[" + to_string(mMatrix[2][0]) + "],[" + to_string(mMatrix[2][1]) + "],[" + to_string(mMatrix[2][2]) + "] " + "],[" + to_string(mMatrix[2][3]) + "]\n";
	message += "[" + to_string(mMatrix[3][0]) + "],[" + to_string(mMatrix[3][1]) + "],[" + to_string(mMatrix[3][2]) + "] " + "],[" + to_string(mMatrix[3][3]) + "]]\n";
	MGlobal::displayInfo(MString(message.c_str()));
}

inline MStatus JumpToElement(MArrayDataHandle& hArray, unsigned int index)
{
	MStatus status;
	status = hArray.jumpToElement(index);
	// If the index does not exist
	if (MFAIL(status)) {
		MArrayDataBuilder builder = hArray.builder(&status);
		CHECK_MSTATUS_AND_RETURN_IT(status);
		// Add the default value at the index
		builder.addElement(index, &status);
		CHECK_MSTATUS_AND_RETURN_IT(status);
		status = hArray.set(builder);
		CHECK_MSTATUS_AND_RETURN_IT(status);
		status = hArray.jumpToElement(index);
		CHECK_MSTATUS_AND_RETURN_IT(status);
	}
	return status;
}

inline bool IsPlugConnected(const MObject& mObject, const MObject& mPlug)
{
	MPlug plug(mObject, mPlug);
	return plug.isConnected();
}

inline bool getBoolPlug(const MDagPath& mDagPath, const MObject& mPlug, bool default=false)
{
	MStatus status;
	MObject mObject = mDagPath.node(&status);
	if (status)
	{
		MPlug plug(mObject, mPlug);
		if (!plug.isNull())
		{
			bool value;
			if (plug.getValue(value))
			{
				return value;
			}
		}
	}
	return default;
}

#endif