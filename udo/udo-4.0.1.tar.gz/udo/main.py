#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse 
import os
import random
import sys
import warnings

from pprint import pprint

import asgroup
import config
import deploy
import launchconfig
import util

# top-level commands go here
class Udo:
    # launchconfig
    def lc(self, *args):
        args = list(args)
        if not len(args) or not args[0]:
            print "launchconfig command requires an action. Valid actions are: "
            print " cloudinit (cluster).(role) - view cloud_init bootstrap script"
            print " create (cluster).(role) - create launch configuration"
            print " destroy (cluster).(role) - delete launch configuration"
            return
        action = args.pop(0)

        cluster,role,extra = self.get_cluster_and_role_from_args(*args)

        if not cluster or not role:
            return

        lc = launchconfig.LaunchConfig(cluster, role)

        if action == 'cloudinit':
            cloudinit = lc.cloud_init_script()
            print cloudinit
        elif action == 'create':
            lc.activate()
        elif action == 'destroy':
            lc.deactivate()
        else:
            print "Unrecognized LaunchConfig action"

    # autoscale
    def asg(self, *args):
        args = list(args)
        if not len(args) or not args[0]:
            print "asgroup command requires an action. Valid actions are: "
            print " instances (cluster).(role) - list instances in group"
            print " randomip (cluster).(role) - get an IP address of a host in the group"
            print " create (cluster).(role) - create an autoscale group"
            print " destroy (cluster).(role) - delete an autoscale group and terminate all instances"
            print " reload (cluster).(role) - destroys asgroup and launchconfig, then recreates them"
            print " updatelc (cluster).(role) - generates a new launchconfig version"
            print " scale (cluster).(role) - view current scaling settings"
            print " scale (cluster).(role) (desired) - set desired number of instances"
            return
        action = args.pop(0)

        # TODO: hook up 'list'

        cluster, role, extra = self.get_cluster_and_role_from_args(*args)
        if not cluster or not role:
            return

        ag = asgroup.AutoscaleGroup(cluster, role)

        if not ag.has_valid_role():
            print "Invalid role {} specified for cluster {}".format(role, cluster)
            return

        if action == 'create':
            ag.activate()
        elif action == 'destroy':
            ag.deactivate()
        elif action == 'reload':
            ag.reload()
        elif action == 'updatelc':
            ag.update_lc()
        elif action == 'instances':
            ag.print_instances()
        elif action == 'randomip':
            ips = ag.ip_addresses()
            print(random.choice(ips))
        elif action == 'scale':
            # get scale arg
            if extra:
                scale = int(extra)
                print("in main.py: ag.scale(scale)")
                ag.scale(scale)
            else:
                print("in main.py: ag.get_scale_size()")
                ag.get_scale_size()
        else:
            print "Unrecognized asgroup action {}".format(action)

    # CodeDeploy
    def deploy(self, *args):
        args = list(args)
        if not len(args) or not args[0]:
            print "deploy command requires an action. Valid actions are: "
            print " list applications"
            print " list groups [application]"
            print " list deployments"
            print " list configs"
            print " create (group) (commit_id)"
            print " last [group]"
            print " status deploymentId" # only for debugging
            return
        action = args.pop(0)

        if action == 'list':
            dep = deploy.Deploy()
            if not len(args):
                print "list what? applications, groups, deployments, post or configs?"
                return
            what = args.pop(0)
            if what == 'applications' or what == 'apps':
                dep.list_applications()
            elif what == 'groups':
                # application name?
                application = None
                if len(args):
                    application = args.pop(0)
                dep.list_groups(application)
            elif what == 'configs':
                dep.list_configs()
            elif what == 'deployments':
                dep.list_deployments()
            elif what == 'post':
                dep.list_post_deploy_hooks()
            else:
                print "Unknown list type: {}".format(what)
        elif action == 'create':
            # require group, commit_id
            if len(args) != 2:
                print "deploy create requires group and commit id"
                return
            group = args.pop(0)
            commit_id = args.pop(0)
            dep = deploy.Deploy()
            dep.create(group, commit_id)
        elif action == 'last':
            dep = deploy.Deploy()
            group_name = None
            if len(args) == 1:
                group_name = args.pop(0)
            dep.print_last_deployment(deployment_group_name=group_name)
        elif action == 'status':
            deploymentId = args.pop(0)
            dep = deploy.Deploy()
            print(dep.deployment_status(deploymentId))
        elif action == 'stop':
            dep = deploy.Deploy()
            group_name = None
            if len(args) == 1:
                group_name = args.pop(0)
            dep.stop_deployment(deployment_group_name=group_name)
        elif len(args) == 1:
            # assume we want to create a deployment
            group = action
            commit_id = args.pop(0)
            dep = deploy.Deploy()
            dep.create(group, commit_id)
        else:
            print "Unknown deploy command: {}".format(action)

    def version(self, *args):
        args = list(args)
        print('3.0.2')

    # for testing features
    def test(self, *args):
        args = list(args)
        if not len(args) or not args[0]:
            print "test command requires an action. Valid actions are: "
            print " integrations"
            return
        action = args.pop(0)

        if action == 'integrations':
            util.message_integrations("Testing Udo integrations")
        else:
            print "Unknown test command: {}".format(action)

    # returns cluster_name,role_name,rest_of_args
    def get_cluster_and_role_from_args(self, *args):
        args = list(args)
        # need cluster/role
        if len(args) < 1:
            print "Please specify cluster.role target for this command"
            return None,None,None
        cluster_role = args.pop(0)

        help = "Please specify the target of your action using the format: cluster.role"

        cluster_name = None
        role_name = None
        if '.' in cluster_role:
            # split on .
            cluster_name, role_name = cluster_role.split(".")
            if not cluster_name:
                print("Cluster name not specified.", help)
            if not role_name:
                print("Role name not specified.", help)
        else:
            # assume we're just talking about a cluster with one role
            cluster_name = cluster_role

        cluster = config.get_cluster_config(cluster_name)
        if not cluster:
            print "Unknown cluster {}".format(cluster_name)
            return None,None,None

        roles = cluster.get('roles')
        if not roles:
            print "Invalid configuration for {}: no roles are defined".format(cluster_name)
            return None,None,None

        if not role_name:
            role_names = roles.keys()
            if len(role_names) == 1:
                # assume the only role
                print "No role specified, assuming {}".format(role_names[0])
                role_name = role_names[0]
            else:
                print "Multiple roles available for cluster {}".format(cluster_name)
                for r in role_names:
                    print "  - {}".format(r)
                return None,None,None

        if not role_name in roles:
            print("Role {} not found in cluster {} configuration".format(role_name, cluster_name))
            return None,None,None

        # still stuff?
        extra = None
        if len(args):
            extra = args.pop(0)

        return cluster_name, role_name, extra

def invoke_console():
    # argument parsing
    parser = argparse.ArgumentParser(description='Manage AWS clusters.')
    parser.add_argument('cmd', metavar='command', type=str, nargs='?',
        help='Action to perform. Valid actions: status.')
    parser.add_argument('cmd_args', metavar='args', type=str, nargs='*',
        help='Additional arguments for command.')
    args = parser.parse_args()
    
    if args.cmd not in dir(Udo):
        if args.cmd:
            print "'{}' is not a valid command".format(args.cmd)
        else:
            print "You must specify a command"
        # full command summary
        print """
Valid commands are:
  * lc cloudinit - display cloud-init script
  * lc create - create a launch configuration
  * lc destroy - delete a launch configuration
  * asg instances - print instances in autoscaling groups
  * asg reload - destroy and create an autoscaling group to update the config
  * asg create - create an autoscaling group
  * asg destroy - delete an autoscaling group
  * asg updatelc - updates launchconfiguration in-place
  * asg scale - set desired number of instances
  * asg randomip - print IP address of random host in group
  * deploy list apps - view CodeDeploy applications
  * deploy list groups - view CodeDeploy application deployment groups
  * deploy list deployments - view CodeDeploy deployment statuses
  * deploy list configs - view CodeDeploy configurations
  * deploy list post - view post deploy hooks
  * deploy [create] (group) (commit) - create new deployment for commit on group
  * deploy last - shows status of most recent deployment
  * deploy stop - cancel last deployment
  * version - print udo version
        """
        sys.exit(1)

    # execute cmd
    exe = Udo()
    method = getattr(exe, args.cmd)
    method(*args.cmd_args)

if __name__ == '__main__':
    invoke_console()
