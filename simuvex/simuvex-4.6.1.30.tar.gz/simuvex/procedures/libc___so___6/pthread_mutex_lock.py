import simuvex

######################################
# Doing nothing
######################################

class pthread_mutex_lock(simuvex.SimProcedure):
    def run(self):
        _ = self.arg(0)
        self.ret()
