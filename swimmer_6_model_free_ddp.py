'''
copyright @ Karthikeya S Parunandi - karthikeyasharma91@gmail.com
Model free DDP method with a 6-link swimmer experiment in MuJoCo simulator.

Date: July 6, 2019
'''
#!/usr/bin/env python

import numpy as np
from model_free_DDP import DDP
import time
from mujoco_py import load_model_from_path, MjSim, MjViewer
from ltv_sys_id import ltv_sys_id_class
from params.swimmer6_params import *
import os

class model_free_swimmer_6_DDP(DDP, ltv_sys_id_class):
	
	def __init__(self, initial_state, final_state, MODEL_XML, alpha, horizon, state_dimemsion, control_dimension, Q, Q_final, R):
		
		'''
			Declare the matrices associated with the cost function
		'''
		self.Q = Q
		self.Q_final = Q_final
		self.R = R

		DDP.__init__(self, MODEL_XML, state_dimemsion, control_dimension, alpha, horizon, initial_state, final_state)
		ltv_sys_id_class.__init__(self, MODEL_XML, state_dimemsion, control_dimension, n_samples=feedback_samples_no)

	def state_output(self, state):
		'''
			Given a state in terms of Mujoco's MjSimState format, extract the state as a numpy array, after some preprocessing
		'''
		
		return np.concatenate([state.qpos, state.qvel]).reshape(-1, 1)


	def cost(self, x, u):
		'''
			Incremental cost in terms of state and controls
		'''
		return (((x - self.X_g).T @ self.Q) @ (x - self.X_g)) + (((u.T) @ self.R) @ u)
	
	def cost_final(self, x):
		'''
			Cost in terms of state at the terminal time-step
		'''
		return (((x - self.X_g).T @ self.Q_final) @ (x - self.X_g)) 

	def initialize_traj(self, path=None):

		'''
		Initial guess for the nominal trajectory by default is produced by zero controls
		'''
		if path is None:
			
			for t in range(0, self.N):
				self.U_p[t] = np.random.normal(0, nominal_init_stddev, (self.n_u, 1))	#np.random.normal(0, 0.01, self.n_u).reshape(self.n_u,1)#DM(array[t, 4:6])
			
			np.copyto(self.U_p_temp, self.U_p)
			
			self.forward_pass_sim()
			
			np.copyto(self.X_p_temp, self.X_p)

		else:

			array = np.loadtxt('../rrt_path.txt')
			### INCOMPLETE


if __name__=="__main__":

	# Path of the model file
	path_to_model_free_DDP = "/home/karthikeya/Documents/research/model_free_DDP"
	MODEL_XML = path_to_model_free_DDP + "/models/swimmer6.xml"
	path_to_exp = path_to_model_free_DDP + "/experiments/swimmer6/exp_11"

	path_to_file = path_to_exp + "/swimmer6_policy.txt"
	training_cost_data_file = path_to_exp + "/training_cost_data.txt"
	path_to_data = path_to_exp + "/swimmer6_D2C_DDP_data.txt"


	# Declare other parameters associated with the problem statement
	
	n_iterations = 250
	alpha = 0.3
	
	# Declare the initial state and the final state in the problem
	initial_state = np.zeros((16,1))
	final_state = np.zeros((16,1))
	final_state[0] = 0.5
	final_state[1] = -0.6

	# Initiate the above class that contains objects specific to this problem
	swimmer6 = model_free_swimmer_6_DDP(initial_state, final_state, MODEL_XML, alpha, horizon, state_dimemsion, control_dimension, Q, Q_final, R)

	# ---------------------------------------------------------------------------------------------------------
	# -----------------------------------------------Training---------------------------------------------------
	# ---------------------------------------------------------------------------------------------------------
	# Train the policy

	training_flag_on = False

	if training_flag_on:

		with open(path_to_data, 'w') as f:

			f.write("D2C training performed for an 6-link swimmer task:\n\n")

			f.write("System details : {}\n".format(os.uname().sysname + "--" + os.uname().nodename + "--" + os.uname().release + "--" + os.uname().version + "--" + os.uname().machine))
			f.write("-------------------------------------------------------------\n")

		time_1 = time.time()

		# Run the DDP algorithm
		# To run using our LLS-CD jacobian estimation (faster), make 'finite_difference_gradients_flag = False'
		# To run using forward difference for jacobian estimation (slower), make 'finite_difference_gradients_flag = True'

		swimmer6.iterate_ddp(n_iterations, finite_difference_gradients_flag=False)
		swimmer6.feedback(W_x_LQR, W_u_LQR, W_x_LQR_f)

		time_2 = time.time()

		D2C_algorithm_run_time = time_2 - time_1

		print("D2C-2 algorithm run time taken: ", D2C_algorithm_run_time)
		
		# Save the episodic cost
		with open(training_cost_data_file, 'w') as f:
			for cost in swimmer6.episodic_cost_history:
				f.write("%s\n" % cost)

		# Test the obtained policy
		swimmer6.save_policy(path_to_file)

		with open(path_to_data, 'a') as f:

				f.write("\nTotal time taken: {}\n".format(D2C_algorithm_run_time))
				f.write("------------------------------------------------------------------------------------------------------------------------------------\n")


		print(swimmer6.X_p[-1])
		
		# Plot the episodic cost during the training
		swimmer6.plot_episodic_cost_history(save_to_path=path_to_exp+"/episodic_cost_training.png")
	
	# ---------------------------------------------------------------------------------------------------------
	# -----------------------------------------------Testing---------------------------------------------------
	# ---------------------------------------------------------------------------------------------------------
	# Test the obtained policy

	#swimmer6.test_episode(render=1, path=path_to_file)
	test_flag_on = True

	if test_flag_on:

		f = open(path_to_exp + "/swimmer6_testing_data.txt", "a")

		def frange(start, stop, step):
			i = start
			while i < stop:
				yield i
				i += step
		
		u_max = 12

		try:

			for i in frange(0.40, 1.02, 0.02):

				print(i)
				print("\n")
				terminal_mse = 0
				Var_terminal_mse = 0
				n_samples = 100

				for j in range(n_samples):	

					terminal_state = swimmer6.test_episode(render=0, path=path_to_file, noise_stddev=i*u_max)
					terminal_mse += np.linalg.norm(terminal_state[0:2] - final_state[0:2], axis=0)
					Var_terminal_mse += (np.linalg.norm(terminal_state[0:2] - final_state[0:2], axis=0))**2

				terminal_mse_avg = terminal_mse/n_samples
				Var_terminal_mse_avg = (1/(n_samples*(n_samples-1)))*(n_samples*Var_terminal_mse - terminal_mse**2)

				std_dev_mse = np.sqrt(Var_terminal_mse_avg)

				f.write(str(i)+",\t"+str(terminal_mse_avg[0])+",\t"+str(std_dev_mse[0])+"\n")
		except:

			print("Testing failed!")
			f.close()

		f.close()


