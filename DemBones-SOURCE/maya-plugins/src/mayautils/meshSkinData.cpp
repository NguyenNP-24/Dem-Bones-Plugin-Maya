#include "meshSkinData.h"

MStatus MeshSkinData::setDagPath(const MDagPath& dagPath)
{
	MStatus status;
	m_dagPath.set(dagPath);
	MFnMesh fnMesh(m_dagPath);
	m_numVertices = fnMesh.numVertices();
	return status;
}

void MeshSkinData::clear()
{
	m_influences.clear();
	for (auto it = m_weightData.begin(); it != m_weightData.end(); ++it)
	{
		it->second.clear();
	}
	m_weightData.clear();
}
