# 1匹で作ったものをベースに9匹分コピペできるようにする
SDF0 = """<?xml version="1.0" ?>

<sdf version="1.9">
    <world name="default">
    <physics name="1ms" type="ignored"><max_step_size>0.001</max_step_size></physics>
    <plugin filename="gz-sim-physics-system" name="gz::sim::systems::Physics"/>
    <plugin filename="gz-sim-user-commands-system" name="gz::sim::systems::UserCommands"/>
    <plugin filename="gz-sim-scene-broadcaster-system" name="gz::sim::systems::SceneBroadcaster"/>
    <plugin filename="gz-sim-sensors-system" name="gz::sim::systems::Sensors"><render_engine>ogre2</render_engine></plugin>
    
   <light type="directional" name="sun">
      <pose>0 0 10 0 0 0</pose>
      <diffuse>0.3 0.3 0.3</diffuse>
      <direction>-0.5 -0.5 0.5</direction>
      <cast_shadows>true</cast_shadows>      
   </light>

   
   <model name="ground_plane">
      <static>true</static>
      <link name="link">
         <collision name="collision">
            <geometry><plane><normal>0 0 1</normal></plane></geometry>
         </collision>
         <visual name="visual">
            <geometry><plane><normal>0 0 1</normal><size>20 20</size></plane></geometry>
            <material>
               <ambient>0.5 0.5 0.5 1</ambient>
               <diffuse>0.5 0.5 0.5 1</diffuse>
            </material>
         </visual>
      </link>
   </model>
   """
#      <diffuse>1.0 1.0 1.0 1</diffuse>


SDF_M1 = """
   <model name="mole_board">
      <link name="board">
         <collision name="collision">
            <geometry><box><size>0.4 0.4 0.1</size></box></geometry>
         </collision>
         <visual name="visual">
            <geometry><box><size>0.4 0.4 0.1</size></box></geometry>
            <material>
               <ambient>0.15 0.45 0.15 1</ambient>
               <diffuse>0.15 0.45 0.15 1</diffuse>
            </material>
         </visual>
         <pose>0 0 0.05 0 0 0</pose>
         <inertial>
            <mass>1.0</mass>
            <inertia>
               <ixx>0.1</ixx>
               <iyy>0.1</iyy>
               <izz>0.1</izz>
               <ixy>0</ixy>
               <ixz>0</ixz>
               <iyz>0</iyz>
            </inertia>
         </inertial>
         """


# 　穴番号i, 位置xy に応じて、穴を作成
def make_SDF_hole(i, x, y):
    SDFh = (
        """<visual name="hole"""
        + str(i)
        + """">
    <pose>"""
        + str(x)
        + " "
        + str(y)
        + """ 0.0505 0 0 0</pose>
    <geometry><cylinder><radius>0.043</radius><length>0.001</length></cylinder></geometry>
    <material>               
        <ambient>0 0 0 1</ambient>
        <diffuse>0 0 0 1</diffuse>
    </material>
    </visual>
    """
    )
    return SDFh


SDF_M2 = """      </link>
      <joint name="fix" type="fixed">
         <parent>world</parent>
         <child>board</child>      
      </joint>"""


# 　モグラ番号i, 位置xy に応じて、モグラを作成
def make_SDF_Mole(i, x, y):
    SDF2 = (
        """      <link name="mole_"""
        + str(i)
        + """">
            <collision name="collision">
                <geometry>
                <cylinder>
                    <radius>0.035</radius>
                    <length> 0.08</length>
                </cylinder>
                </geometry>
            </collision>
            <visual name="visual">
                <geometry>
                <cylinder>
                    <radius>0.035</radius>
                    <length>0.08</length>
                </cylinder>
                </geometry>
                <material>
                <ambient>0.6 0.3 0.1 1</ambient>
                <diffuse>0.6 0.3 0.1 1</diffuse>
                </material>
            </visual>
            <pose>"""
        + str(x)
        + " "
        + str(y)
        + """ 0.05 0 0 0</pose>
            <inertial>
                <mass>0.3</mass>
                <inertia>
                <ixx>0.0002</ixx>
                <iyy>0.0002</iyy>
                <izz>0.0002</izz>
                <ixy>0</ixy>
                <ixz>0</ixz>
                <iyz>0</iyz>
                </inertia>
            </inertial>
        </link>
        <joint name="mole_"""
        + str(i)
        + """_joint" type="prismatic">
            <parent>board</parent>
            <child>mole_"""
        + str(i)
        + """</child>     
            <axis>
                <xyz>0 0 1</xyz>
                <limit><lower>0</lower><upper>0.07</upper></limit>
            </axis>  
        </joint>
        <plugin filename="gz-sim-joint-position-controller-system" name="gz::sim::systems::JointPositionController">
         <joint_name>mole_"""
        + str(i)
        + """_joint</joint_name>
         <topic>/mole_"""
        + str(i)
        + """/cmd_pos</topic>
         <p_gain>1000</p_gain>
         <d_gain>35</d_gain>
         <cmd_max>30</cmd_max>
         <cmd_min>-30</cmd_min>
      </plugin>"""
    )

    return SDF2


SDF_M3 = """
   </model>"""

# モグラ台作成ここまで

# ここからハンマー
SDF_Hammer = """
    <model name="gantry">   
        <link name="base">
        <pose>0 0 0 0 0 0</pose>
        <inertial>
            <mass>0.5</mass>
            <inertia>
                <ixx>0.1</ixx>
                <iyy>0.1</iyy>
                <izz>0.1</izz>
                <ixy>0</ixy>
                <ixz>0</ixz>
                <iyz>0</iyz>
            </inertia>
        </inertial>
        </link>
        <joint name="base_fix" type="fixed">
            <parent>world</parent><child>base</child>
        </joint>

        <link name="carriage_x"> 
        <pose>0 0 0 0 0 0</pose>
        <inertial>
            <mass>0.5</mass>
            <inertia>
                <ixx>0.1</ixx>
                <iyy>0.1</iyy>
                <izz>0.1</izz>
                <ixy>0</ixy>
                <ixz>0</ixz>
                <iyz>0</iyz>
            </inertia>
        </inertial>
        </link>
        <joint name="x_joint" type="prismatic">
            <parent>base</parent><child>carriage_x</child>
            <axis><xyz>1 0 0</xyz>
            <limit><lower>-0.15</lower><upper>0.30</upper></limit>
            </axis>
        </joint>

        <link name="carriage_y">
        <pose>0 0 0 0 0 0</pose>
        <inertial>
            <mass>0.5</mass>
            <inertia>
                <ixx>0.1</ixx>
                <iyy>0.1</iyy>
                <izz>0.1</izz>
                <ixy>0</ixy>
                <ixz>0</ixz>
                <iyz>0</iyz>
            </inertia>
        </inertial>
        </link>
        <joint name="y_joint" type="prismatic">
            <parent>carriage_x</parent><child>carriage_y</child>
            <axis><xyz>0 1 0</xyz>
            <limit><lower>-0.15</lower><upper>0.15</upper></limit>
            </axis>
        </joint>

    <link name="hammer">
        <collision name="collision">
            <geometry>
                <cylinder>
                    <radius>0.03</radius>
                    <length>0.04</length>
                </cylinder>
            </geometry>
        </collision>
        <visual name="visual">
            <geometry>
                <cylinder>
                    <radius>0.03</radius>
                    <length>0.04</length>
                 </cylinder>
            </geometry>
            <material>
                <ambient>0 0 1.0 1</ambient>
                <diffuse>0 0 1.0 1</diffuse>
            </material>
        </visual>
        <pose>0 0 0.27 0 0 0</pose>
        <inertial>
            <mass>0.3</mass>
            <inertia>
               <ixx>0.0002</ixx>
               <iyy>0.0002</iyy>
               <izz>0.0002</izz>
               <ixy>0</ixy>
               <ixz>0</ixz>
               <iyz>0</iyz>
            </inertia>
        </inertial>
    </link>
    <joint name="z_joint" type="prismatic">
        <parent>carriage_y</parent><child>hammer</child>
        <axis><xyz>0 0 1</xyz>
        <limit><lower>-0.15</lower><upper>0.0</upper></limit>
        </axis>
    </joint>

    <plugin filename="gz-sim-joint-position-controller-system" name="gz::sim::systems::JointPositionController">
        <joint_name>x_joint</joint_name>
        <topic>/gantry/x</topic>
        <p_gain>1000</p_gain>
        <d_gain>80</d_gain>
        <cmd_max>100</cmd_max>
        <cmd_min>-100</cmd_min>
    </plugin>
    <plugin filename="gz-sim-joint-position-controller-system" name="gz::sim::systems::JointPositionController">
        <joint_name>y_joint</joint_name>
        <topic>/gantry/y</topic>
        <p_gain>1000</p_gain>
        <d_gain>80</d_gain>
        <cmd_max>100</cmd_max>
        <cmd_min>-100</cmd_min>
    </plugin>
    <plugin filename="gz-sim-joint-position-controller-system" name="gz::sim::systems::JointPositionController">
        <joint_name>z_joint</joint_name>
        <topic>/gantry/z</topic>
        <p_gain>1000</p_gain>
        <d_gain>80</d_gain>
        <cmd_max>100</cmd_max>
        <cmd_min>-100</cmd_min>
    </plugin>

</model>
"""

# ここからカメラ
SDF_Cammer = """
   <model name="top_camera">
        <static>true</static>
        <link name="link">
         <pose>0 0 0.8 0 1.5708 0</pose>
         <sensor name="camera" type="camera">
            <topic>/top_camera/image</topic>
            <update_rate>10</update_rate>
            <always_on>true</always_on><visualize>true</visualize>
            <camera>
                <horizontal_fov>0.8</horizontal_fov>
                <image><width>320</width><height>320</height><format>R8G8B8</format></image>
                <clip><near>0.05</near><far>3</far></clip>
            </camera>
         </sensor>
        </link>
   </model>
"""

SDF_END = """
   </world>
</sdf>"""

with open("test.sdf", "w", encoding="utf-8") as f:
    f.write(
        SDF0
        + SDF_M1
        + make_SDF_hole(0, -0.1, -0.1)
        + make_SDF_hole(1, -0.1, 0)
        + make_SDF_hole(2, -0.1, 0.1)
        + make_SDF_hole(3, 0, -0.1)
        + make_SDF_hole(4, 0, 0)
        + make_SDF_hole(5, 0, 0.1)
        + make_SDF_hole(6, 0.1, -0.1)
        + make_SDF_hole(7, 0.1, 0)
        + make_SDF_hole(8, 0.1, 0.1)
        + SDF_M2
        + make_SDF_Mole(0, -0.1, -0.1)
        + make_SDF_Mole(1, -0.1, 0)
        + make_SDF_Mole(2, -0.1, 0.1)
        + make_SDF_Mole(3, 0, -0.1)
        + make_SDF_Mole(4, 0, 0)
        + make_SDF_Mole(5, 0, 0.1)
        + make_SDF_Mole(6, 0.1, -0.1)
        + make_SDF_Mole(7, 0.1, 0)
        + make_SDF_Mole(8, 0.1, 0.1)
        + SDF_M3
        + SDF_Hammer
        + SDF_Cammer
        + SDF_END
    )
