import maya.api.OpenMaya as om
import maya.cmds as cd

class MAYA_Model:
    def __init__(self,modelData,basic):
        self.basic = basic
        self.modelData = modelData
        self.faceVertCounts = None
        self.defaultName = "ImportModel"
        self.name = self.defaultName
        self.use_fvArray = False
    
    def Create(self):
        self.basic.BIG_Comment("モデルを作成")

        self.basic.Small_Comment("メッシュの作成")
        self._CreateMesh()
        self.basic.Small_Comment("マテリアルの作成")
        self._CreateMaterial()
        
        self.basic.Small_Comment("モデルの作成終了")

    def _CreateMesh(self):
        # 頂点データをMAYAの配列に入れる
        pointArray = om.MFloatPointArray()
        for i in self.modelData.vertexList:
            point = om.MFloatPoint(i.position[0], i.position[1], i.position[2])
            pointArray.append(point)

        # 各フェースの頂点数
        faceVertArray = om.MIntArray()
        if self.use_fvArray: # 引数で各フェースの頂点数の配列を受け取っていたら
            for i in self.faceVertCounts:
                faceVertArray.append(i)
        else: # すべてのフェースで一定の頂点数の場合
            face_num = int(len(self.modelData.vert_indexList) / self.faceVertCounts)
            for i in range(face_num):
                faceVertArray.append(self.faceVertCounts)

        # インデックスデータをMAYAの配列に入れる
        indexArray = om.MIntArray()
        for i in self.modelData.vert_indexList:
            indexArray.append(i)

        # UV情報を入れる
        uArray = om.MFloatArray()
        vArray = om.MFloatArray()
        for i in self.modelData.vertexList:
            uArray.append(i.uv[0])
            vArray.append(i.uv[1])
        
        # 法線情報を入れる
        nomalArray = om.MVectorArray()
        for i in self.modelData.vertexList:
            nomal = om.MVector(i.nomal[0],i.nomal[1],i.nomal[2])
            nomalArray.append(nomal)

        if len(self.name) != len(self.name.encode("utf-8")):
            self.basic.Small_Comment("モデル名「"+self.name+"」は使用できないので「"+self.defaultName+"」に置き換えられます")
            self.name = self.defaultName

        # ノードを作成
        self.shape_node = om.MFnMesh()
        tf_obj = self.shape_node.create(pointArray,faceVertArray,indexArray,uArray,vArray)
        self.shape_node.assignUVs(faceVertArray,indexArray)
        self.shape_node.setVertexNormals(nomalArray,om.MIntArray(range(len(self.modelData.vertexList))))
        self.tf_node = om.MFnTransform(tf_obj) # create関数で生まれたオブジェクトをノードに変換
        self.tf_node.setName(self.name)
        self.name = self.tf_node.name()
        self.shape_node.setName(self.name+'Shape')

    def _CreateMaterial(self):
        # 貼り付けるフェースを数える
        faceStart = 0
        faceEnd = 0
        # マテリアルを順番に作成
        for i,mat in enumerate(self.modelData.matList):
            try:
                # マテリアル名を使用可能なものに変更
                if len(mat.matName) != len(mat.matName.encode("utf-8")):
                    matName = self.name + "_Mat" + str(i)
                else:
                    matName = mat.matName
                
                # マテリアルを作成
                matName = cd.shadingNode('lambert',asShader=1,name=matName)
                self.basic.Small_Comment("マテリアル名「"+mat.matName+"」は使用できないので"+matName+"に置き換えられます")
            except:
                # マテリアル名を使用可能なものに変更
                matName = self.name + "_Mat" + str(i)
                # マテリアルを作成
                matName = cd.shadingNode('lambert',asShader=1,name=matName)
                self.basic.Small_Comment("マテリアル名「"+mat.matName+"」は使用できないので"+matName+"に置き換えられます")

            # アトリビュートを設定
            color = mat.diffuse[:3]
            ambColor = mat.ambient
            cd.setAttr(matName+'.color',*color,typ='double3')
            cd.setAttr(matName+'.ambientColor',*ambColor,typ='double3')
            
            # テクスチャを割り当て
            if mat.texIndex != -1:
                tex_node = cd.shadingNode("file",asTexture=True, name=matName+"_texture")
                cd.setAttr(tex_node+".fileTextureName",self.modelData.texPaths[mat.texIndex],type="string")
                cd.connectAttr(tex_node+".outColor",matName+".color",force=True)

            # マテリアルを割り当て
            mat_sg = cd.sets(renderable=1,noSurfaceShader=1,empty=1,name=matName+'SG')
            cd.connectAttr(matName+'.outColor',mat_sg+'.surfaceShader', force=True)

            # フェースを割り当て
            faceEnd = int(faceStart + (mat.verNum/3) - 1)
            cd.sets(self.name+".f[%s:%s]"%(faceStart,faceEnd),forceElement=mat_sg)
            faceStart += int(mat.verNum/3)