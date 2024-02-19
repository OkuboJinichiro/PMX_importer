from . import MyPackage as mp
basic = mp.Basic()

# ===== GUIのボタンにコマンドを関連付け =====
class GUI(mp.MAYA_GUI):
    def ButtonCmds(self, id="test"):
        basic.Small_Comment(id+"を実行")
        
        if id == "ModelImport":
            ModelIMPORT(self.Modelpath,self.ModelExt)

        basic.BIG_Comment("実行終了")

# ===== エントリポイント =====
def main():
    gui = GUI()

# モデルインポート
def ModelIMPORT(path,ext):
    if ext == ".pmx":
        # PMXモデルを解析
        importModel = mp.PMX_Model(path,basic)
        # MAYAでモデルを作成
        mayaModel = mp.MAYA_Model(importModel,basic)
        mayaModel.faceVertCounts = 3
        mayaModel.name = importModel.header.modelName
        mayaModel.Create()
    else:
        basic.Small_Comment("対応したファイル形式ではありません")