from ._base_task import Base_Task
from .utils import *
from copy import deepcopy
import os

class swap_blocks(Base_Task):
    
    def setup_demo(self, **kwags):
        super()._init_task_env_(**kwags)

    def load_actors(self):
        x = -0.14
        basket_lst = []
        for i in range(3):
            basket_pose = rand_pose(
                xlim=[x, x],
                ylim=[-0.15, -0.15],
                qpos=[0.5, 0.5, 0.5, 0.5],
            )
            x += 0.14
            basket_lst.append(basket_pose)
        self.baskets=[]
        for i in range(3):
            basket = create_actor(
                scene=self,
                pose=basket_lst[i],
                modelname="002_breadbasket",
                convex=True,
                model_id="1",
                is_static=True,
            )
            self.baskets.append(basket)
        
        self.backset_name = ['left', 'middle', 'right']
        
        block_half_size = 0.015
        x_block = -0.14
        blocks_lst = []
        for i in range(3):
            block_pose = rand_pose(
                xlim=[x_block-0.005, x_block+0.005],
                ylim=[-0.15-0.005, -0.15+0.005],
                zlim=[0.75 + block_half_size],
                qpos=[1,0,0,0],
                rotate_rand=True,
                rotate_lim=[0, 0, 0.75],
            )
            x_block += 0.14
            blocks_lst.append(deepcopy(block_pose))

        def create_block(block_pose):
            return create_box(
                scene=self,
                pose=block_pose,
                half_size=(block_half_size, block_half_size, block_half_size),
                color=(1,0,0),
                name="box",
            )
        mask = [False, False, False]
        self.with_block_basket_idx_1 = np.random.randint(0,3)
        mask[self.with_block_basket_idx_1] = True
        remaining = [i for i, v in enumerate(mask) if not v]
        self.with_block_basket_idx_2 = np.random.choice(remaining)
        mask[self.with_block_basket_idx_2] = True
        self.empty_basket_idx = mask.index(False)
        self.block3_pose = blocks_lst[self.empty_basket_idx]
        self.block1 = create_block(blocks_lst[self.with_block_basket_idx_1])
        self.block2 = create_block(blocks_lst[self.with_block_basket_idx_2])
        self.flag = True

        self.button = rand_create_sapien_urdf_obj(
            scene=self,
            modelname="005_button",
            modelid=10124,
            xlim=[-0.0, -0.0],
            ylim=[-0.28, -0.28],
            rotate_rand=False,
            rotate_lim=[0, 0, np.pi / 16],
            qpos=[1, 0, 0, 0],
            fix_root_link=True,
        )
        self.button.set_mass(0.0001, ['button_cap'])
        self.set_button_unpressed(self.button)
        self.press_cnt = 0
        self.press_flag = False
        self._last_success_debug_signature = None

    def get_current_button_value(self, button_name, button_actor, joint_name="button_joint", target=0.0):
        if button_name == 'button':
            button_actor = button_actor
        else:
            button_actor = self.check_button
        art = button_actor.actor if hasattr(button_actor, "actor") else button_actor      
        joints = art.get_active_joints()   
        joint_names = [j.get_name() for j in joints]    
        idx = joint_names.index(joint_name)
        qpos = art.get_qpos()
        return qpos[idx]

    def set_button_unpressed(self, button_actor, joint_name="button_joint", target=0.0): 
        art = button_actor.actor if hasattr(button_actor, "actor") else button_actor   
        joints = art.get_active_joints()   
        joint_names = [j.get_name() for j in joints]    
        idx = joint_names.index(joint_name)
        qpos = art.get_qpos()
        qpos[idx] = target   
        art.set_qpos(qpos) 
        joints[idx].set_drive_target(target)
    
    def check_button_pressed(self, button_actor, joint_name="button_joint", threshold=-0.005): 
        art = button_actor.actor if hasattr(button_actor, "actor") else button_actor   
        joints = art.get_active_joints()   
        joint_names = [j.get_name() for j in joints]    
        idx = joint_names.index(joint_name) 
        qpos = art.get_qpos()
        if qpos[idx] < threshold:
            return True
        else:
            return False
        
    def update_button_reset(self, button_actor, flag_attr, joint_name="button_joint", threshold=-0.001):
        art = button_actor.actor if hasattr(button_actor, "actor") else button_actor
        joints = art.get_active_joints()
        joint_names = [j.get_name() for j in joints]
        idx = joint_names.index(joint_name)

        qpos = art.get_qpos()
        if qpos[idx] > threshold:
            setattr(self, flag_attr, False)

    def check_button_pressed(self, button_actor, joint_name="button_joint", threshold=-0.005): 
        art = button_actor.actor if hasattr(button_actor, "actor") else button_actor   
        joints = art.get_active_joints()   
        joint_names = [j.get_name() for j in joints]    
        idx = joint_names.index(joint_name) 
        qpos = art.get_qpos()
        if qpos[idx] < threshold:
            return True
        else:
            return False
        
    def update_button_reset(self, button_actor, flag_attr, joint_name="button_joint", threshold=-0.001):
        art = button_actor.actor if hasattr(button_actor, "actor") else button_actor
        joints = art.get_active_joints()
        joint_names = [j.get_name() for j in joints]
        idx = joint_names.index(joint_name)

        qpos = art.get_qpos()
        if qpos[idx] > threshold:
            setattr(self, flag_attr, False)

    def update_press_success(self, button_actor, flag_attr, cnt_attr):
        if self.check_button_pressed(button_actor) and not getattr(self, flag_attr):
            setattr(self, flag_attr, True)
            setattr(self, cnt_attr, getattr(self, cnt_attr) + 1)
        
    def play_once(self):
        basket1_center_pose = self.baskets[self.with_block_basket_idx_1].get_functional_point(0)
        basket2_center_pose = self.baskets[self.with_block_basket_idx_2].get_functional_point(0)
        basket3_center_pose = self.baskets[self.empty_basket_idx].get_functional_point(0)

        arm_tag = self.choose_arm(self.baskets[self.with_block_basket_idx_1], self.baskets[self.empty_basket_idx])
        self.move(self.grasp_actor(self.block1, arm_tag=arm_tag, pre_grasp_dis=0.09, grasp_dis=0.02), language_annotation=f"Use {arm_tag} arm to pick up the {self.get_block_pose(1)} block and move it to the {self.backset_name[self.empty_basket_idx]} tray.")
        self.move(self.move_by_displacement(arm_tag=arm_tag, z=0.06), language_annotation=f"Use {arm_tag} arm to pick up the {self.get_block_pose(1)} block and move it to the {self.backset_name[self.empty_basket_idx]} tray.")
        self.move(self.place_actor(self.block1, arm_tag=arm_tag, functional_point_id=2, constrain="free", target_pose=basket3_center_pose, pre_dis=0.07), language_annotation=f"Use {arm_tag} arm to pick up the {self.get_block_pose(1)} block and move it to the {self.backset_name[self.empty_basket_idx]} tray.")
        self.is_two_blocks(self.block1,self.block2)
        self.move(self.back_to_origin(arm_tag=arm_tag), language_annotation=f"Use {arm_tag} arm to pick up the {self.get_block_pose(1)} block and move it to the {self.backset_name[self.empty_basket_idx]} tray.")

        arm_tag = self.choose_arm(self.baskets[self.with_block_basket_idx_1], self.baskets[self.with_block_basket_idx_2])
        self.move(self.grasp_actor(self.block2, arm_tag=arm_tag, pre_grasp_dis=0.09, grasp_dis=0.02), language_annotation=f"Use {arm_tag} arm to pick up the {self.get_block_pose(2)} block and move it to the {self.backset_name[self.with_block_basket_idx_1]} tray.")
        self.move(self.move_by_displacement(arm_tag=arm_tag, z=0.06), language_annotation=f"Use {arm_tag} arm to pick up the {self.get_block_pose(2)} block and move it to the {self.backset_name[self.with_block_basket_idx_1]} tray.")
        self.move(self.place_actor(self.block2, arm_tag=arm_tag, functional_point_id=2, constrain="free", target_pose=basket1_center_pose), language_annotation=f"Use {arm_tag} arm to pick up the {self.get_block_pose(2)} block and move it to the {self.backset_name[self.with_block_basket_idx_1]} tray.")
        self.is_two_blocks(self.block1,self.block2)
        self.move(self.back_to_origin(arm_tag=arm_tag), language_annotation=f"Use {arm_tag} arm to pick up the {self.get_block_pose(2)} block and move it to the {self.backset_name[self.with_block_basket_idx_1]} tray.")
        
        arm_tag = self.choose_arm(self.baskets[self.with_block_basket_idx_2], self.baskets[self.empty_basket_idx])
        self.move(self.grasp_actor(self.block1, arm_tag=arm_tag, pre_grasp_dis=0.09, grasp_dis=0.02), language_annotation=f"Use {arm_tag} arm to pick up the {self.get_block_pose(1)} block and move it to the {self.backset_name[self.with_block_basket_idx_2]} tray.")
        self.move(self.move_by_displacement(arm_tag=arm_tag, z=0.06), language_annotation=f"Use {arm_tag} arm to pick up the {self.get_block_pose(1)} block and move it to the {self.backset_name[self.with_block_basket_idx_2]} tray.")
        self.move(self.place_actor(self.block1, arm_tag=arm_tag, functional_point_id=2, constrain="free", target_pose=basket2_center_pose), language_annotation=f"Use {arm_tag} arm to pick up the {self.get_block_pose(1)} block and move it to the {self.backset_name[self.with_block_basket_idx_2]} tray.")
        self.is_two_blocks(self.block1,self.block2)
        self.move(self.back_to_origin(arm_tag=arm_tag), language_annotation=f"Use {arm_tag} arm to pick up the {self.get_block_pose(1)} block and move it to the {self.backset_name[self.with_block_basket_idx_2]} tray.")
        self.move(self.grasp_actor(self.button, arm_tag="left", pre_grasp_dis=0.08, grasp_dis=0.08,contact_point_id=0,),
                   language_annotation='Press the button.')
        self.move(self.move_by_displacement(arm_tag="left", z=-0.04), language_annotation='Press the button.')
        self.update_press_success(self.button, "press_flag", "press_cnt")
        self.info["info"] = {}
        return self.info

    def is_two_blocks(self, block1, block2):
        block1_pose = block1.get_pose().p
        block2_pose = block2.get_pose().p
        if np.abs(block1_pose[0] - block2_pose[0]) < 0.03 and np.abs(block1_pose[2] - block2_pose[2]) < 0.01:
            self.flag = False
        
    def get_block_pose(self, block_id):
        block1_pose = self.block1.get_pose().p
        block2_pose = self.block2.get_pose().p
        if block_id == 1:
            return "left" if block1_pose[0] < block2_pose[0] else "right"
        if block_id == 2:
            return "left" if block1_pose[0] > block2_pose[0] else "right"
                
    def choose_arm(self, basket1, basket2):
        if basket1.get_pose().p[0] > 0.12 or basket2.get_pose().p[0] > 0.12:
            arm = "right"
        elif basket1.get_pose().p[0] <= -0.12 or basket2.get_pose().p[0] <= -0.12:
            arm = "left"
        return arm

    def _debug_check_success(
        self,
        success,
        basket1_pose,
        basket2_pose,
        block1_pose,
        block2_pose,
        checks,
        button_value,
    ):
        if os.environ.get("RMBENCH_SWAP_DEBUG_SUCCESS", "0").lower() not in ("1", "true", "yes", "on"):
            return

        signature = (
            int(getattr(self, "take_action_cnt", -1)),
            bool(success),
            tuple(bool(checks[k]) for k in sorted(checks)),
            int(self.press_cnt),
            bool(self.press_flag),
            bool(self.flag),
        )
        if signature == self._last_success_debug_signature:
            return
        self._last_success_debug_signature = signature

        b2_to_basket1 = np.abs(basket1_pose[:2] - block2_pose[:2])
        b1_to_basket2 = np.abs(basket2_pose[:2] - block1_pose[:2])
        print("\n[swap_blocks debug] check_success")
        print(f"  action_step={getattr(self, 'take_action_cnt', None)} success={bool(success)} max_reward={self.max_reward}")
        print(
            "  basket indices: "
            f"block1_start={self.with_block_basket_idx_1} "
            f"block2_start={self.with_block_basket_idx_2} "
            f"empty_start={self.empty_basket_idx}"
        )
        print(f"  basket1_pose={np.round(basket1_pose, 4)}")
        print(f"  basket2_pose={np.round(basket2_pose, 4)}")
        print(f"  block1_pose ={np.round(block1_pose, 4)}  target=basket2")
        print(f"  block2_pose ={np.round(block2_pose, 4)}  target=basket1")
        print(
            "  block2->basket1: "
            f"dx={b2_to_basket1[0]:.4f}<0.04={checks['block2_x']} "
            f"dy={b2_to_basket1[1]:.4f}<0.06={checks['block2_y']} "
            f"z={block2_pose[2]:.4f}<0.765={checks['block2_z']}"
        )
        print(
            "  block1->basket2: "
            f"dx={b1_to_basket2[0]:.4f}<0.04={checks['block1_x']} "
            f"dy={b1_to_basket2[1]:.4f}<0.06={checks['block1_y']} "
            f"z={block1_pose[2]:.4f}<0.765={checks['block1_z']}"
        )
        print(
            "  other: "
            f"gripper_close={checks['gripper_close']} "
            f"flag_no_overlap={checks['flag']} "
            f"press_cnt={self.press_cnt} "
            f"press_flag={self.press_flag} "
            f"button_qpos={button_value:.4f}"
        )

    def check_success(self):
        self.update_button_reset(self.button, "press_flag")
        self.update_press_success(self.button, "press_flag", "press_cnt")
        button_value = self.get_current_button_value("button", self.button)
        self.set_button_unpressed(self.button, target=min(0.0, button_value+0.002))
        basket1_pose = self.baskets[self.with_block_basket_idx_1].get_pose().p
        basket2_pose = self.baskets[self.with_block_basket_idx_2].get_pose().p
        block1_pose = self.block1.get_pose().p
        block2_pose = self.block2.get_pose().p
        self.is_two_blocks(self.block1, self.block2)
        checks = {
            "block2_x": np.abs(basket1_pose[0] - block2_pose[0]) < 0.04,
            "block2_y": np.abs(basket1_pose[1] - block2_pose[1]) < 0.06,
            "block2_z": block2_pose[2] < 0.765,
            "block1_x": np.abs(basket2_pose[0] - block1_pose[0]) < 0.04,
            "block1_y": np.abs(basket2_pose[1] - block1_pose[1]) < 0.06,
            "block1_z": block1_pose[2] < 0.765,
            "gripper_close": self.is_left_gripper_close() or self.is_right_gripper_close(),
            "flag": self.flag,
            "press_cnt": self.press_cnt == 1,
            "press_flag": self.press_flag,
        }
        success = all(checks.values())
        self.max_reward = max(self.max_reward, float(success))
        self._debug_check_success(
            success,
            basket1_pose,
            basket2_pose,
            block1_pose,
            block2_pose,
            checks,
            button_value,
        )
        
        return success
