from struct import *
import os

# ========== PMX構造体 ==========
# ヘッダー
class PMXHeader:
    def __init__(self):
        # マジックナンバー
        self.PMX = ""
        self.version = None
        # データ列
        self.datasize = None
        self.encode = None
        # モデル情報
        self.modelName = None
        self.modelName_EN = None
        self.comment = None
        self.comment_EN = None
    def DataSet(self,data):
        self.adduv_num = data[1]
        self.vert_IndexSize = data[2]
        self.tex_IndexSize = data[3]
        self.mat_IndexSize = data[4]
        self.bone_IndexSize = data[5]
        self.morf_IndexSize = data[6]
        self.rigid_IndexSize = data[7]

        self.vert_Index_fc = self.IndexSize_to_FormatChar(data[2])
        self.tex_Index_fc = self.IndexSize_to_FormatChar(data[3])
        self.mat_Index_fc = self.IndexSize_to_FormatChar(data[4])
        self.bone_Index_fc = self.IndexSize_to_FormatChar(data[5])
        self.morf_Index_fc = self.IndexSize_to_FormatChar(data[6])
        self.rigid_Index_fc = self.IndexSize_to_FormatChar(data[7])
    def IndexSize_to_FormatChar(self,indexSize):
        if indexSize == 1:
            return "b"
        if indexSize == 2:
            return "h"
        if indexSize == 4:
            return "i"
    
# 頂点
class Vertex:
    def __init__(self):
        self.position = None
        self.nomal = None
        self.uv = None
        self.adduv = None
        self.weightType = None
        self.bone = None
        self.weight = None
        self.sdef = None
        self.edge_mag = None

# マテリアル
class Material:
    def __init__(self) -> None:
        self.matName = None
        self.matName_EN = None
    def SetData(self,data) -> None:
        self.diffuse = [data[0],data[1],data[2],data[3]]
        self.specular = [data[4],data[5],data[6]]
        self.specularity = data[7]
        self.ambient = [data[8],data[9],data[10]]
        self.bifFlag = self.BitFlagChack(data[11])
        self.edgeColor = [data[12],data[13],data[14],data[15]]
        self.edgeSize = data[16]
        self.texIndex = data[17]
        self.sphTexIndex = data[18]
        self.sphereMode = data[19]
        self.toonFlag = data[20]
        self.toonIndex = data[21]
        self.memo = data[22]
        self.verNum = data[23]
    def BitFlagChack(self,bit):
        flag = [False,False,False,False,False]
        # 0x01:両面描画
        if bit & 0x01 != 0:
            flag[0] = True
        # 0x02:地面影
        if bit & 0x02 != 0:
            flag[1] = True
        # 0x04:セルフシャドウマップへの描画
        if bit & 0x04 != 0:
            flag[2] = True
        # 0x08:セルフシャドウの描画
        if bit & 0x08 != 0:
            flag[3] = True
        # 0x10:エッジ描画
        if bit & 0x10 != 0:
            flag[4] = True
        return flag

# ========== PMX読み込みクラス ==========
class PMX_Model:
    def __init__(self,path,basic):
        # コメントのテンプレートクラス
        self.basic = basic
        
        basic.BIG_Comment("PMXをロード")
        self.path = path
        self.DirPath = os.path.dirname(self.path) + "/"
        self.f = open(self.path,"rb")

        basic.Small_Comment("ヘッダーのロード")
        self._HeaderLoad()
        basic.Small_Comment("頂点のロード")
        self._VertexLoad()
        basic.Small_Comment("フェースのロード")
        self._FaceLoad()
        basic.Small_Comment("テクスチャパスのロード")
        self._TexLoad()
        basic.Small_Comment("マテリアルのロード")
        self._MatLoad()
        
        self.f.close()
        basic.Small_Comment("PMXのロード終了")

    # ===== ヘッダー読み込み =====
    def _HeaderLoad(self):
        self.header = PMXHeader() # 構造体初期化
        f = self.f # コード短縮用
        
        # データ列の手前までロード
        buffer = f.read(9)
        data = unpack("ccccfB",buffer)
        # ヘッダーに代入
        for i in range(4):
            self.header.PMX += data[i].decode("ascii")
        self.header.version = data[4]
        self.header.datasize = data[5]

        # データ列をロード
        buffer = f.read(self.header.datasize)
        formatchar = "B" * self.header.datasize
        data = unpack(formatchar,buffer)
        # データを代入
        if data[0] == 0: # エンコード方式(0:utf-16,1:utf-8)
            self.header.encode = "utf-16"
        elif data[0] == 1:
            self.header.encode = "utf-8"
        self.header.DataSet(data)

        # モデル情報
        self.header.modelName = self._TextBuf()
        self.header.modelName_EN = self._TextBuf()
        self.header.comment = self._TextBuf()
        self.header.comment_EN = self._TextBuf()

    # ===== 頂点読み込み =====
    def _VertexLoad(self):
        f = self.f # コード短縮用
        
        # 頂点数を読み込み
        buffer = f.read(4)
        self.vertexNum = (unpack("i",buffer))[0]

        # ボーンインデックスの型を設定
        bone_IndexSize = self.header.bone_IndexSize
        bone_Index_fc = self.header.bone_Index_fc

        # 頂点数だけ頂点を読み込み
        self.vertexList = []
        for i in range(self.vertexNum):
            self.vertexList.append(Vertex())

        for i in self.vertexList:
            # 位置
            buffer = f.read(12)
            pos = list(unpack("fff",buffer))
            for j in range(3):
                pos[j] *= 8
            pos[2] *= -1
            i.position = pos
            # 法線
            buffer = f.read(12)
            nomal = list(unpack("fff",buffer))
            nomal[2] *= -1
            i.nomal = nomal
            # UV
            buffer = f.read(8)
            i.uv = list(unpack("ff",buffer))
            i.uv[1] *= -1
            i.uv[1] += 1
            # 追加UV
            i.adduv = []
            for j in range(self.header.adduv_num):
                buffer = f.read(16)
                i.adduv.append(list(unpack("ffff",buffer)))
            # ウェイト
            buffer = f.read(1)
            i.weightType = (unpack("B",buffer))[0]
            if i.weightType == 0: #BDEF1
                buffer = f.read(bone_IndexSize)
                i.bone = list(unpack(bone_Index_fc,buffer))
                i.weight = [1.0]
            elif i.weightType == 1: #BDEF2
                formatchar = bone_Index_fc * 2
                buffer = f.read(bone_IndexSize * 2)
                i.bone = list(unpack(formatchar,buffer))
                buffer = f.read(4)
                i.weight = list(unpack("f",buffer))
                i.weight.append(1.0 - i.weight[0])
            elif i.weightType == 2: #BDEF4
                formatchar = bone_Index_fc * 4
                buffer = f.read(bone_IndexSize * 4)
                i.bone = list(unpack(formatchar,buffer))
                buffer = f.read(16)
                i.weight = list(unpack("ffff",buffer))
            elif i.weightType == 3: #SDEF
                formatchar = bone_Index_fc * 2
                buffer = f.read(bone_IndexSize * 2)
                i.bone = list(unpack(formatchar,buffer))
                buffer = f.read(4)
                i.weight = list(unpack("f",buffer))
                i.weight.append(1.0 - i.weight[0])
                buffer = f.read(36)
                data = unpack("fffffffff",buffer)
                i.sdef = {
                    "C":{"x":data[0],"y":data[1],"z":data[2]},
                    "R0":{"x":data[3],"y":data[4],"z":data[5]},
                    "R1":{"x":data[6],"y":data[7],"z":data[8]}
                }
            # エッジ倍率
            buffer = f.read(4)
            i.edge_mag = (unpack("f",buffer))[0]

    # ===== フェース(頂点インデックス)読み込み =====
    def _FaceLoad(self):
        vert_IndexSize = self.header.vert_IndexSize
        vert_Index_fc = "" # fc = formatcharacter
        if vert_IndexSize == 1:
            vert_Index_fc = "B"
        if vert_IndexSize == 2:
            vert_Index_fc = "H"
        if vert_IndexSize == 4:
            vert_Index_fc = "i"

        vert_index_num = (unpack("i",self.f.read(4)))[0]
        fc = vert_Index_fc * vert_index_num
        self.vert_indexList = list(unpack(fc,self.f.read(vert_IndexSize * vert_index_num)))

        for i in range(int(vert_index_num/3)):
            i2 = self.vert_indexList[i*3+1]
            i3 = self.vert_indexList[i*3+2]
            self.vert_indexList[i*3+1] = i3
            self.vert_indexList[i*3+2] = i2

    # ===== テクスチャ読み込み =====
    def _TexLoad(self):
        f = self.f # コード短縮用

        # テクスチャ数を読み込み
        buffer = f.read(4)
        self.texNum = (unpack("i",buffer))[0]

        self.texPaths = []
        for i in range(self.texNum):
            self.texPaths.append(self.DirPath + self._TextBuf())

    # ===== マテリアル読み込み =====
    def _MatLoad(self):
        f = self.f # コード短縮用
        self.matNum = (unpack("i",f.read(4)))[0]

        # マテリアル数のインスタンスを作成
        self.matList = []
        for i in range(self.matNum):
            self.matList.append(Material())

        for i in self.matList:
            # マテリアル名
            i.matName = self._TextBuf()
            i.matName_EN = self._TextBuf()

            # データをまとめて読み込み
            TIS = self.header.tex_IndexSize
            TFC = self.header.tex_Index_fc
            bitsize = 16+12+4+12+1
            fc = "ffff"+"fff"+"f"+"fff"+"B"
            data = unpack(fc,f.read(bitsize))
            bitsize = 16+4+TIS+TIS+1+1
            fc = "ffff"+"f"+TFC+TFC+"B"+"B"
            data2 = unpack(fc,f.read(bitsize))
            if data2[8] == 0:
                data3 = unpack(TFC,f.read(TIS))
            elif data2[8] == 1:
                data3 = unpack("B",f.read(1))
            data4 = (self._TextBuf(),)
            data5 = unpack("i",f.read(4))

            i.SetData(data + data2 + data3 + data4 + data5)

    # ===== テキストバッファー読み込み =====
    def _TextBuf(self):
        buffer =  self.f.read(4)
        size = (unpack("i",buffer))[0]
        buffer = self.f.read(size)
        return buffer.decode(self.header.encode)
    
# デバック用
if __name__ == "__main__":
    class Basic:
        def BIG_Comment(self,text):
            print("\r\n# ===== "+text+" =====\r\n")
        def Small_Comment(self,text):
            print("# "+text)
    eula = PMX_Model("C:/Google/My/MAYA/Gensin/assets/Test/Fischl/Fischl.pmx",Basic())
    # for i in eula.vertexList:
    #     print(i.weight)
    # print(eula.matNum)
    # for i in eula.matList:
    #     print(i.matName)
    # for i in eula.texPaths:
    #     print(i)