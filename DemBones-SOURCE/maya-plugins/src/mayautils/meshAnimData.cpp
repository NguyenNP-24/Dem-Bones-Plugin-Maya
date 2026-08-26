#include "meshAnimData.h"

MStatus MeshAnimData::setDagPath(const MDagPath& dagPath)
{
	MStatus status;
	m_dagPath.set(dagPath);
	MFnMesh fnMesh(m_dagPath);
	m_numVertices = fnMesh.numVertices();
	return status;
}

MStatus MeshAnimData::setBindVertices()
{
	MStatus status;
	MFnMesh fnMesh(m_dagPath);
	// The frame we are here is gonna be the bind position
	status = fnMesh.getPoints(m_vertices, MSpace::kWorld);
	CHECK_MSTATUS_AND_RETURN_IT(status);
	return status;
}

MStatus MeshAnimData::setExampleVertices(int currFrame)
{
	MStatus status;
	MFnMesh fnMesh(m_dagPath);
	status = fnMesh.getPoints(m_animVertices[currFrame], MSpace::kWorld);
	CHECK_MSTATUS_AND_RETURN_IT(status);
	return status;
}

void MeshAnimData::clear()
{
	m_vertices.clear();
	m_animVertices.clear();
}