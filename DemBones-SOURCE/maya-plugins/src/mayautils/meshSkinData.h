#ifndef __MAYA_MESH_SKIN_DATA_H__
#define __MAYA_MESH_ANIM_DATA_H__

#include <maya/MFnMesh.h>
#include <maya/MDagPath.h>
#include <maya/MDagPathArray.h>

#include <vector>
#include <map>

struct JointWeightData
{
	unsigned int m_influenceIndex;
	float m_weight;
};

class MeshSkinData
{
public:
	MDagPath m_dagPath;
	unsigned int m_numVertices;
	MDagPathArray m_influences;
	std::map<int, std::vector<JointWeightData>> m_weightData;

	MeshSkinData() {}
	~MeshSkinData() {}
	MStatus setDagPath(const MDagPath& dagPath);
	void clear();
};

#endif