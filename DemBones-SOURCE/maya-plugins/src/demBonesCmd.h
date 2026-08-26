#ifndef __DEM_BONES_CMD_H__
#define __DEM_BONES_CMD_H__

#include <maya/MGlobal.h>
#include <maya/MSyntax.h>
#include <maya/MArgList.h>
#include <maya/MArgDatabase.h>
#include <maya/MDGModifier.h>
#include <maya/MPxCommand.h>
#include <maya/MDagPath.h>
#include <maya/MDagPathArray.h>

#include <vector>

#include "demBonesCustom.h"

#include "mayautils/meshAnimData.h"
#include "mayautils/jointAnimData.h"
#include "mayautils/meshSkinData.h"

class DemBonesCmd : public MPxCommand {
public:

    static MString typeName;

    DemBonesCmd();
    virtual ~DemBonesCmd();
    virtual MStatus doIt(const MArgList& argList);
    virtual MStatus redoIt();
    virtual bool isUndoable() const;
    static void* creator();
    static MSyntax createSyntax();

private:
    MStatus solveWeights();
    MStatus solveTransformsAndWeights();
    MStatus createJoints(DemBonesCustom &demBones, const MDagPath &parent, MDagPathArray &joints);


    int m_startFrame;
    int m_endFrame;
    MDagPath m_sourceMesh;
    MDagPath m_targetMesh;

    MStringArray m_jointNames;
    int m_numBones;

    bool m_globalItersSet; int m_globalIters;
    bool m_weightItersSet; int m_weightIters;
    bool m_transItersSet; int m_transIters;
    bool m_patienceSet; int m_patience = 3;
    bool m_toleranceSet; double m_tolerance = 1e-3;
    
    bool m_reuseSkeletonSet; bool m_reuseSkeleton = false;

    MeshSkinData m_skinData;
    MeshAnimData m_meshData;
    std::vector<JointAnimData> m_skelAnimData;

    MDagPathArray m_joints;
};

#endif