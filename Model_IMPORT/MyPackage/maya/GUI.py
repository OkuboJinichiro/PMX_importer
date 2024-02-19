import maya.cmds as cd
import os

class MAYA_GUI:
    def __init__(self) -> None:
        cd.window(title = "モデルインポート",
                mxb = False,
                width = 300,
                height = 10)
        cd.columnLayout(adj = True)
        cd.text(label= "(PMX2.0に対応)")
        
        cd.rowLayout(nc=2,adj=True)
        self.textField = cd.textField(h=20,tx="ファイルパスを指定")
        cd.button(l = "...",w=20,c = self.FileSelect)
        cd.setParent("..")

        cd.button(l = "モデル読み込み",c = self.ModelImport)
        cd.showWindow()

    # 引数を指定できるようにボタンにワンクッション置く
    # クラスを継承してメインファイルにて関数を指定
    def ButtonCmds(self,id="test") -> None:
        print(id+"を実行")
    
    def FileSelect(self,e):
        self.Modelpath = cd.fileDialog(mode = 0,dm=cd.workspace(q=True,active=True)+"/assets/*.pmx")
        cd.textField(self.textField,e=True,tx=self.Modelpath)
        if "?" in self.Modelpath:
            print("使用できない文字が存在します")

    def ModelImport(self,e):
        self.Modelpath = cd.textField(self.textField,q=True,tx=True)
        self.ModelExt = (os.path.splitext(self.Modelpath))[1]
        self.ButtonCmds(id = "ModelImport")