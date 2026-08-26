#include <string>

#include <maya/MFnPlugin.h>
#include "demBonesCmd.h"

static const char* kAuthor = "Gorka Mendieta";
static const char* kVersion = "0.1";

MStatus initializePlugin(MObject ob)
{
	MStatus status;
	MFnPlugin fnPlugin(ob, kAuthor, kVersion, "Any");

	status = fnPlugin.registerCommand(DemBonesCmd::typeName, DemBonesCmd::creator, DemBonesCmd::createSyntax);
	if (MFAIL(status))
	{
		status.perror("Failed to register command demBones.");
		return status;
	}
		
	return MS::kSuccess;
}

MStatus uninitializePlugin(MObject ob)
{
	MStatus status;
	MFnPlugin fnPlugin(ob);

	status = fnPlugin.deregisterCommand(DemBonesCmd::typeName);
	if (MFAIL(status))
	{
		status.perror("Failed to deregister command demBones.");
	}

	return status;
}