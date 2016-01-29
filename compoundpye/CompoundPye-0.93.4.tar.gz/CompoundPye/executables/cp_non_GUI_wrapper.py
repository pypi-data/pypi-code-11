#! python

'''
Wrapper to create a System object (with Circuit and Surroundings) as created with a GUI run. Using this object in a script rather than in the GUI allows for a lot more freedom and automization,
e.g. to run the simulation several times with different stimulus speeds.
Intended to be used with circuit_object.pkl and surroundings_object.pkl as created
by the GUI (run.py).
'''

from CompoundPye import system
import pickle


def create_system(path,skip_relax=True):
    """
    Create a System object as defined by several files in the given folder.
    
    All required files should be created by a successful run of a simulation with the GUI:
    - values.pkl
    - circuit_object.pkl
    - surroundings_object.pkl
    
    @param path Path to the folder.
    """
    with open(path+'/values.pkl','rb') as f:
        values=pickle.load(f)

    dt=values['system_values']['dt']
    relax_time=values['system_values']['relaxation_time']
    relax_intensity=values['system_values']['relaxation_intensity']
    relax_mode=values['system_values']['relax_calculation']

    if skip_relax:
        with open(path+'/circuit_object_relaxed.pkl','rb') as f:
            circ=pickle.load(f)
        relax_time=0.0
    else:
        with open(path+'/circuit_object.pkl','rb') as f:
            circ=pickle.load(f)
        
    with open(path+'/surroundings_object.pkl','rb') as f:
        surr=pickle.load(f)

    
    s=system.System(circ,surr,dt,relax_time,relax_intensity,relax_mode)

    return s,values,dt


if __name__=="__main__":

    

    import sys
    import os

    import numpy as np



    if len(sys.argv)<3:
        sys.stdout("ERROR: execute with two parameters:\n\t1. path to the output folder, which needs to contain one template folder named 'template'\n\t2. list of movement speeds for the first stimulus-object.")

    else:
        temp_path=sys.argv[1]+'template'
        path=sys.argv[1]
        

        exec("v="+sys.argv[2])


        


        def single_process(template,v_i,stim_indices=[0],neuron_save_indices=[],neuron_save_labels=[],sensor_save_indices=[],intensities_save_interval=None,skip_relax=True):

            

            folder=path+'out_'+str(v_i)
            os.system('mkdir '+folder)

            s,values,dt=create_system(temp_path,skip_relax)

            t_end=float(values['system_values']['sim_time'])


            for i in stim_indices:
            
                stim=s.surroundings.stimuli[i]
                stim.velocity=np.array([v_i*s.surroundings.n_pixel[0],0.0])

            if neuron_save_indices==[] and neuron_save_labels==[]:
                comps=s.circuit.components
                neuron_save_indices=range(len(s.circuit.components))
            else:
                comps=[]
                if neuron_save_indices!=[]:
                    comps=comps+[s.circuit.components[c] for c in neuron_save_indices]
                if neuron_save_labels!=[]:
                    for c in s.circuit.components:
                        if neuron_save_labels.count(c.label):
                            comps.append(c)
            
            
            if sensor_save_indices==[]:
                sensors=s.circuit.sensors
                sensor_save_indices=range(len(s.circuit.sensors))
            else:
                sensors=[s.circuit.sensors[sen] for sen in sensor_save_indices]

            if intensities_save_interval==None:
                record_interval=30000
            else:
                record_interval=int(intensities_save_interval)

            #labels=[(str(c.group_label),str(c.label)) for c in s.circuit.components]
            labels=[(str(c.group_label),str(c.label)) for c in comps]
            

            dtypes=[(lbl[0]+' '+lbl[1],'float') for lbl in labels]
            dtype_sensors=[(str(sens.label),'float') for sens in sensors]


            # creates the arrays to store the Circuit's output
            output_comp=np.zeros((int(t_end/dt)+1,),dtype=dtypes)
            output_sens=np.zeros((int(t_end/dt)+1,),dtype=dtype_sensors)

            output_surround=np.zeros((int((int(t_end/dt))/record_interval)+1,s.surroundings.intensities.shape[0],s.surroundings.intensities.shape[1]))
            i=0
            t=0

            f_out=open(path+'/log_'+str(v_i),'w')
            

            #sys.stdout.write('------ t='+str(t))

            

            while t<t_end:
                
                #print '------ '+str(i)
                if i%500==0:
                    f_out.write('\r')
                    f_out.write('------ t='+str(t))
                    f_out.flush()
                new_comp_values=np.zeros(len(comps))
                
                for j in range(0,new_comp_values.shape[0]):
                    new_comp_values[j]=comps[j].get_output()
                
                

                new_sens_values=np.zeros(len(sensors))
                for k in range(0,new_sens_values.shape[0]):
                    new_sens_values[k]=sensors[k].get_value()
                    #if i%200==0:
                    #print new_sens_values
                output_comp[i]=new_comp_values
                output_sens[i]=new_sens_values

                if i%record_interval==0:
                    output_surround[i/record_interval]=s.surroundings.intensities[:,:,0]
                    #print int(i*record_freq)
                s.update()

                t+=dt
                i+=1
        
            #print "I run through the while loop!"

            f_out.close()

            # saves the output arrays in the folder you specified in the GUI's output-tab.
            np.save(folder+'/neurons.npy',output_comp)
            np.save(folder+'/sensors.npy',output_sens)
            np.save(folder+'/intensities.npy',output_surround)
            np.save(folder+'/time.npy',np.arange(0,i+1)*dt)

            with open(folder+'/values.pkl','wb') as f:
                pickle.dump(values,f,pickle.HIGHEST_PROTOCOL)


            del output_surround
            del output_sens
            del output_comp

            sys.stdout.write("done with v="+str(v_i)+"\n")

            #print "I run through the function!"

            return True
            

        n=1
        if sys.argv.count('-n'):
            n=int(sys.argv[sys.argv.index('-n')+1])
        
        stim_indices=[0]
        if sys.argv.count('-i'):
            exec("stim_indices="+sys.argv[sys.argv.index('-i')+1])

        neuron_save_indices=[]
        if sys.argv.count('--neurons'):
            exec("neuron_save_indices="+sys.argv[sys.argv.index('--neurons')+1])

        neuron_save_labels=[]
        if sys.argv.count('--neurons-by-labels'):
            exec("neuron_save_labels="+sys.argv[sys.argv.index('--neurons-by-labels')+1])
            

        sensor_save_indices=[]
        if sys.argv.count('--sensors'):
            exec("sensor_save_indices="+sys.argv[sys.argv.index('--sensors')+1])

        intensities_save_interval=None
        if sys.argv.count('--intensities'):
            exec("intensities_save_interval="+sys.argv[sys.argv.index('--intensities')+1])

        skip_relax=True
        if sys.argv.count('--run-relaxation'):
            skip_relax=False

        import multiprocessing as mp

        pool=mp.Pool(processes=n)
        
        '''
        outputs=mp.Queue()
        processes=[mp.Process(target=single_process, args=(temp_path,v_i)) for v_i in v]
        

        for p in processes:
            p.start()

        for p in processes:
            p.join()

        results=[outputs.get() for p in processes]
        '''

        results=[pool.apply_async(single_process, args=(temp_path,v_i,stim_indices,neuron_save_indices,neuron_save_labels,sensor_save_indices,intensities_save_interval,skip_relax)) for v_i in v]
        #results=[pool.apply_async(single_process, args=(temp_path,v_i)) for v_i in v]
        
        results=[p.get() for p in results]

        os.system("rm "+path+"/log_*")

        print results
        


