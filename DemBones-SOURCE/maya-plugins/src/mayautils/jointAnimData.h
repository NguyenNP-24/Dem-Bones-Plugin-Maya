#ifndef __MAYA_JOINT_ANIM_DATA_H__
#define __MAYA_JOINT_ANIM_DATA_H__

#include <maya/MDagPath.h>
#include <maya/MMatrix.h>

#include <map>

class JointAnimData
{
public:
	MDagPath m_dagPath;
	MMatrix m_bindMatrix;
	MMatrix m_bindInvMatrix;
	std::map<int, MMatrix> m_animMatrices;		// Matrices for all the example frames
	std::map<int, MMatrix> m_animInvMatrices;

	JointAnimData() {}
	~JointAnimData() {}
	MStatus setDagPath(const MDagPath& dagPath);
	MStatus setBindMatrix();
	MStatus setExampleMatrix(int currFrame);
	void clear();
};

#endif

