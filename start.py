import sys
import maya.cmds as cd

projectPath = cd.workspace(q=True,active=True)
sys.path.append(projectPath+"/scripts")

import Model_IMPORT
Model_IMPORT.main()