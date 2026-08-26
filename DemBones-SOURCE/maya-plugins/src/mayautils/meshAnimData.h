#ifndef __MAYA_MESH_ANIM_DATA_H__
#define __MAYA_MESH_ANIM_DATA_H__

#include <maya/MFnMesh.h>
#include <maya/MDagPath.h>
#include <maya/MPointArray.h>

#include <map>

class MeshAnimData
{
public:
	MDagPath m_dagPath;
	unsigned int m_numVertices;
	MPointArray m_vertices; // Vertex positions for bind pose
	std::map<int, MPointArray> m_animVertices; // Vertex positions for all the example frames

	MeshAnimData() {}
	~MeshAnimData() {}
	MStatus setDagPath(const MDagPath& dagPath);
	MStatus setBindVertices();
	MStatus setExampleVertices(int currFrame);
	void clear();
};

#endif
