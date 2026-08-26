
#include "jointAnimData.h"

MStatus JointAnimData::setDagPath(const MDagPath& dagPath)
{
	MStatus status;
	status = m_dagPath.set(dagPath);
	CHECK_MSTATUS_AND_RETURN_IT(status);
	return status;
}

MStatus JointAnimData::setBindMatrix()
{
	MStatus status;
	m_bindMatrix = m_dagPath.inclusiveMatrix();
	m_bindInvMatrix = m_dagPath.inclusiveMatrixInverse();
	return status;
}

MStatus JointAnimData::setExampleMatrix(int currFrame)
{
	MStatus status;
	m_animMatrices[currFrame] = m_dagPath.inclusiveMatrix();
	m_animInvMatrices[currFrame] = m_dagPath.inclusiveMatrixInverse();
	return status;
}

void JointAnimData::clear()
{
	m_animMatrices.clear();
}