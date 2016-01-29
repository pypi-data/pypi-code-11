# Auto-generated by BabelAPI, do not modify.

from abc import ABCMeta, abstractmethod

from . import babel_validators as bv

from . import (
    async,
    auth,
    files,
    sharing,
    team,
    users,
)


class DropboxTeamBase(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def request(self):
        pass

    # ------------------------------------------
    # Routes in team namespace

    def team_devices_list_member_devices(self,
                                         team_member_id,
                                         include_web_sessions=True,
                                         include_desktop_clients=True,
                                         include_mobile_clients=True):
        """
        List all device sessions of a team's member.

        :param str team_member_id: The team's member id
        :param bool include_web_sessions: Whether to list web sessions of the
            team's member
        :param bool include_desktop_clients: Whether to list linked desktop
            devices of the team's member
        :param bool include_mobile_clients: Whether to list linked mobile
            devices of the team's member
        :rtype: :class:`dropbox.team.ListMemberDevicesResult`
        :raises: :class:`dropbox.exceptions.ApiError`

        If this raises, ApiError.reason is of type:
            :class:`dropbox.team.ListMemberDevicesError`
        """
        arg = team.ListMemberDevicesArg(team_member_id,
                                        include_web_sessions,
                                        include_desktop_clients,
                                        include_mobile_clients)
        r = self.request(
            'api',
            'team/devices/list_member_devices',
            'rpc',
            bv.Struct(team.ListMemberDevicesArg),
            bv.Struct(team.ListMemberDevicesResult),
            bv.Union(team.ListMemberDevicesError),
            arg,
            None,
        )
        return r

    def team_devices_list_team_devices(self,
                                       cursor=None,
                                       include_web_sessions=True,
                                       include_desktop_clients=True,
                                       include_mobile_clients=True):
        """
        List all device sessions of a team.

        :param Nullable cursor: At the first call to the
            :meth:`devices_list_team_devices` the cursor shouldn't be passed.
            Then, if the result of the call includes a cursor, the following
            requests should include the received cursors in order to receive the
            next sub list of team devices
        :param bool include_web_sessions: Whether to list web sessions of the
            team members
        :param bool include_desktop_clients: Whether to list desktop clients of
            the team members
        :param bool include_mobile_clients: Whether to list mobile clients of
            the team members
        :rtype: :class:`dropbox.team.ListTeamDevicesResult`
        :raises: :class:`dropbox.exceptions.ApiError`

        If this raises, ApiError.reason is of type:
            :class:`dropbox.team.ListTeamDevicesError`
        """
        arg = team.ListTeamDevicesArg(cursor,
                                      include_web_sessions,
                                      include_desktop_clients,
                                      include_mobile_clients)
        r = self.request(
            'api',
            'team/devices/list_team_devices',
            'rpc',
            bv.Struct(team.ListTeamDevicesArg),
            bv.Struct(team.ListTeamDevicesResult),
            bv.Union(team.ListTeamDevicesError),
            arg,
            None,
        )
        return r

    def team_devices_revoke_device_session(self,
                                           arg):
        """
        Revoke a device session of a team's member

        :type arg: :class:`dropbox.team.RevokeDeviceSessionArg`
        :rtype: None
        :raises: :class:`dropbox.exceptions.ApiError`

        If this raises, ApiError.reason is of type:
            :class:`dropbox.team.RevokeDeviceSessionError`
        """
        r = self.request(
            'api',
            'team/devices/revoke_device_session',
            'rpc',
            bv.Union(team.RevokeDeviceSessionArg),
            bv.Void(),
            bv.Union(team.RevokeDeviceSessionError),
            arg,
            None,
        )
        return None

    def team_devices_revoke_device_session_batch(self,
                                                 revoke_devices):
        """
        Revoke a list of device sessions of team members

        :type revoke_devices: list
        :rtype: :class:`dropbox.team.RevokeDeviceSessionBatchResult`
        :raises: :class:`dropbox.exceptions.ApiError`

        If this raises, ApiError.reason is of type:
            :class:`dropbox.team.RevokeDeviceSessionBatchError`
        """
        arg = team.RevokeDeviceSessionBatchArg(revoke_devices)
        r = self.request(
            'api',
            'team/devices/revoke_device_session_batch',
            'rpc',
            bv.Struct(team.RevokeDeviceSessionBatchArg),
            bv.Struct(team.RevokeDeviceSessionBatchResult),
            bv.Union(team.RevokeDeviceSessionBatchError),
            arg,
            None,
        )
        return r

    def team_get_info(self):
        """
        Retrieves information about a team.

        :rtype: :class:`dropbox.team.TeamGetInfoResult`
        """
        arg = None
        r = self.request(
            'api',
            'team/get_info',
            'rpc',
            bv.Void(),
            bv.Struct(team.TeamGetInfoResult),
            bv.Void(),
            arg,
            None,
        )
        return r

    def team_groups_create(self,
                           group_name,
                           group_external_id=None):
        """
        Creates a new, empty group, with a requested name. Permission : Team
        member management

        :param str group_name: Group name.
        :param Nullable group_external_id: Optional argument. The creator of a
            team can associate an arbitrary external ID to the group.
        :rtype: :class:`dropbox.team.GroupFullInfo`
        :raises: :class:`dropbox.exceptions.ApiError`

        If this raises, ApiError.reason is of type:
            :class:`dropbox.team.GroupCreateError`
        """
        arg = team.GroupCreateArg(group_name,
                                  group_external_id)
        r = self.request(
            'api',
            'team/groups/create',
            'rpc',
            bv.Struct(team.GroupCreateArg),
            bv.Struct(team.GroupFullInfo),
            bv.Union(team.GroupCreateError),
            arg,
            None,
        )
        return r

    def team_groups_delete(self,
                           arg):
        """
        Deletes a group. The group is deleted immediately. However the revoking
        of group-owned resources may take additional time. Use the
        :meth:`groups_job_status_get` to determine whether this process has
        completed. Permission : Team member management

        :param arg: Argument for selecting a single group, either by group_id or
            by external group ID.
        :type arg: :class:`dropbox.team.GroupSelector`
        :rtype: :class:`dropbox.team.LaunchEmptyResult`
        :raises: :class:`dropbox.exceptions.ApiError`

        If this raises, ApiError.reason is of type:
            :class:`dropbox.team.GroupDeleteError`
        """
        r = self.request(
            'api',
            'team/groups/delete',
            'rpc',
            bv.Union(team.GroupSelector),
            bv.Union(async.LaunchEmptyResult),
            bv.Union(team.GroupDeleteError),
            arg,
            None,
        )
        return r

    def team_groups_get_info(self,
                             arg):
        """
        Retrieves information about one or more groups. Permission : Team
        Information

        :param arg: Argument for selecting a list of groups, either by
            group_ids, or external group IDs.
        :type arg: :class:`dropbox.team.GroupsSelector`
        :rtype: list
        :raises: :class:`dropbox.exceptions.ApiError`

        If this raises, ApiError.reason is of type:
            :class:`dropbox.team.GroupsGetInfoError`
        """
        r = self.request(
            'api',
            'team/groups/get_info',
            'rpc',
            bv.Union(team.GroupsSelector),
            bv.List(bv.Union(team.GroupsGetInfoItem)),
            bv.Union(team.GroupsGetInfoError),
            arg,
            None,
        )
        return r

    def team_groups_job_status_get(self,
                                   async_job_id):
        """
        Once an async_job_id is returned from :meth:`groups_delete`,
        :meth:`groups_members_add` , or :meth:`groups_members_remove` use this
        method to poll the status of granting/revoking group members' access to
        group-owned resources. Permission : Team member management

        :param str async_job_id: Id of the asynchronous job. This is the value
            of a response returned from the method that launched the job.
        :rtype: :class:`dropbox.team.PollEmptyResult`
        :raises: :class:`dropbox.exceptions.ApiError`

        If this raises, ApiError.reason is of type:
            :class:`dropbox.team.GroupsPollError`
        """
        arg = async.PollArg(async_job_id)
        r = self.request(
            'api',
            'team/groups/job_status/get',
            'rpc',
            bv.Struct(async.PollArg),
            bv.Union(async.PollEmptyResult),
            bv.Union(team.GroupsPollError),
            arg,
            None,
        )
        return r

    def team_groups_list(self,
                         limit=1000):
        """
        Lists groups on a team. Permission : Team Information

        :param long limit: Number of results to return per call.
        :rtype: :class:`dropbox.team.GroupsListResult`
        """
        arg = team.GroupsListArg(limit)
        r = self.request(
            'api',
            'team/groups/list',
            'rpc',
            bv.Struct(team.GroupsListArg),
            bv.Struct(team.GroupsListResult),
            bv.Void(),
            arg,
            None,
        )
        return r

    def team_groups_list_continue(self,
                                  cursor):
        """
        Once a cursor has been retrieved from :meth:`groups_list`, use this to
        paginate through all groups. Permission : Team information

        :param str cursor: Indicates from what point to get the next set of
            groups.
        :rtype: :class:`dropbox.team.GroupsListResult`
        :raises: :class:`dropbox.exceptions.ApiError`

        If this raises, ApiError.reason is of type:
            :class:`dropbox.team.GroupsListContinueError`
        """
        arg = team.GroupsListContinueArg(cursor)
        r = self.request(
            'api',
            'team/groups/list/continue',
            'rpc',
            bv.Struct(team.GroupsListContinueArg),
            bv.Struct(team.GroupsListResult),
            bv.Union(team.GroupsListContinueError),
            arg,
            None,
        )
        return r

    def team_groups_members_add(self,
                                group,
                                members):
        """
        Adds members to a group. The members are added immediately. However the
        granting of group-owned resources may take additional time. Use the
        :meth:`groups_job_status_get` to determine whether this process has
        completed. Permission : Team member management

        :param group: Group to which users will be added.
        :type group: :class:`dropbox.team.GroupSelector`
        :param list members: List of users to be added to the group.
        :rtype: :class:`dropbox.team.GroupMembersChangeResult`
        :raises: :class:`dropbox.exceptions.ApiError`

        If this raises, ApiError.reason is of type:
            :class:`dropbox.team.GroupMembersAddError`
        """
        arg = team.GroupMembersAddArg(group,
                                      members)
        r = self.request(
            'api',
            'team/groups/members/add',
            'rpc',
            bv.Struct(team.GroupMembersAddArg),
            bv.Struct(team.GroupMembersChangeResult),
            bv.Union(team.GroupMembersAddError),
            arg,
            None,
        )
        return r

    def team_groups_members_remove(self,
                                   group,
                                   users):
        """
        Removes members from a group. The members are removed immediately.
        However the revoking of group-owned resources may take additional time.
        Use the :meth:`groups_job_status_get` to determine whether this process
        has completed. Permission : Team member management

        :type group: :class:`dropbox.team.GroupSelector`
        :type users: list
        :rtype: :class:`dropbox.team.GroupMembersChangeResult`
        :raises: :class:`dropbox.exceptions.ApiError`

        If this raises, ApiError.reason is of type:
            :class:`dropbox.team.GroupMembersRemoveError`
        """
        arg = team.GroupMembersRemoveArg(group,
                                         users)
        r = self.request(
            'api',
            'team/groups/members/remove',
            'rpc',
            bv.Struct(team.GroupMembersRemoveArg),
            bv.Struct(team.GroupMembersChangeResult),
            bv.Union(team.GroupMembersRemoveError),
            arg,
            None,
        )
        return r

    def team_groups_members_set_access_type(self,
                                            group,
                                            user,
                                            access_type):
        """
        Sets a member's access type in a group. Permission : Team member
        management

        :param access_type: New group access type the user will have.
        :type access_type: :class:`dropbox.team.GroupAccessType`
        :rtype: list
        :raises: :class:`dropbox.exceptions.ApiError`

        If this raises, ApiError.reason is of type:
            :class:`dropbox.team.GroupMemberSelectorError`
        """
        arg = team.GroupMembersSetAccessTypeArg(group,
                                                user,
                                                access_type)
        r = self.request(
            'api',
            'team/groups/members/set_access_type',
            'rpc',
            bv.Struct(team.GroupMembersSetAccessTypeArg),
            bv.List(bv.Union(team.GroupsGetInfoItem)),
            bv.Union(team.GroupMemberSelectorError),
            arg,
            None,
        )
        return r

    def team_groups_update(self,
                           group,
                           new_group_name=None,
                           new_group_external_id=None):
        """
        Updates a group's name and/or external ID. Permission : Team member
        management

        :param group: Specify a group.
        :type group: :class:`dropbox.team.GroupSelector`
        :param Nullable new_group_name: Optional argument. Set group name to
            this if provided.
        :param Nullable new_group_external_id: Optional argument. New group
            external ID. If the argument is None, the group's external_id won't
            be updated. If the argument is empty string, the group's external id
            will be cleared.
        :rtype: :class:`dropbox.team.GroupFullInfo`
        :raises: :class:`dropbox.exceptions.ApiError`

        If this raises, ApiError.reason is of type:
            :class:`dropbox.team.GroupUpdateError`
        """
        arg = team.GroupUpdateArgs(group,
                                   new_group_name,
                                   new_group_external_id)
        r = self.request(
            'api',
            'team/groups/update',
            'rpc',
            bv.Struct(team.GroupUpdateArgs),
            bv.Struct(team.GroupFullInfo),
            bv.Union(team.GroupUpdateError),
            arg,
            None,
        )
        return r

    def team_linked_apps_list_member_linked_apps(self,
                                                 team_member_id):
        """
        List all linked applications of the team member. Note, this endpoint
        doesn't list any team-linked applications.

        :param str team_member_id: The team member id
        :rtype: :class:`dropbox.team.ListMemberAppsResult`
        :raises: :class:`dropbox.exceptions.ApiError`

        If this raises, ApiError.reason is of type:
            :class:`dropbox.team.ListMemberAppsError`
        """
        arg = team.ListMemberAppsArg(team_member_id)
        r = self.request(
            'api',
            'team/linked_apps/list_member_linked_apps',
            'rpc',
            bv.Struct(team.ListMemberAppsArg),
            bv.Struct(team.ListMemberAppsResult),
            bv.Union(team.ListMemberAppsError),
            arg,
            None,
        )
        return r

    def team_linked_apps_list_team_linked_apps(self,
                                               cursor=None):
        """
        List all applications linked to the team members' accounts. Note, this
        endpoint doesn't list any team-linked applications.

        :param Nullable cursor: At the first call to the
            :meth:`linked_apps_list_team_linked_apps` the cursor shouldn't be
            passed. Then, if the result of the call includes a cursor, the
            following requests should include the received cursors in order to
            receive the next sub list of the team applications
        :rtype: :class:`dropbox.team.ListTeamAppsResult`
        :raises: :class:`dropbox.exceptions.ApiError`

        If this raises, ApiError.reason is of type:
            :class:`dropbox.team.ListTeamAppsError`
        """
        arg = team.ListTeamAppsArg(cursor)
        r = self.request(
            'api',
            'team/linked_apps/list_team_linked_apps',
            'rpc',
            bv.Struct(team.ListTeamAppsArg),
            bv.Struct(team.ListTeamAppsResult),
            bv.Union(team.ListTeamAppsError),
            arg,
            None,
        )
        return r

    def team_linked_apps_revoke_linked_app(self,
                                           app_id,
                                           team_member_id,
                                           keep_app_folder=True):
        """
        Revoke a linked application of the team member

        :param str app_id: The application's unique id
        :param str team_member_id: The unique id of the member owning the device
        :param bool keep_app_folder: Whether to keep the application dedicated
            folder (in case the application uses  one)
        :rtype: None
        :raises: :class:`dropbox.exceptions.ApiError`

        If this raises, ApiError.reason is of type:
            :class:`dropbox.team.RevokeLinkedAppError`
        """
        arg = team.RevokeLinkedApiAppArg(app_id,
                                         team_member_id,
                                         keep_app_folder)
        r = self.request(
            'api',
            'team/linked_apps/revoke_linked_app',
            'rpc',
            bv.Struct(team.RevokeLinkedApiAppArg),
            bv.Void(),
            bv.Union(team.RevokeLinkedAppError),
            arg,
            None,
        )
        return None

    def team_linked_apps_revoke_linked_app_batch(self,
                                                 revoke_linked_app):
        """
        Revoke a list of linked applications of the team members

        :type revoke_linked_app: list
        :rtype: :class:`dropbox.team.RevokeLinkedAppBatchResult`
        :raises: :class:`dropbox.exceptions.ApiError`

        If this raises, ApiError.reason is of type:
            :class:`dropbox.team.RevokeLinkedAppBatchError`
        """
        arg = team.RevokeLinkedApiAppBatchArg(revoke_linked_app)
        r = self.request(
            'api',
            'team/linked_apps/revoke_linked_app_batch',
            'rpc',
            bv.Struct(team.RevokeLinkedApiAppBatchArg),
            bv.Struct(team.RevokeLinkedAppBatchResult),
            bv.Union(team.RevokeLinkedAppBatchError),
            arg,
            None,
        )
        return r

    def team_members_add(self,
                         new_members,
                         force_async=False):
        """
        Adds members to a team. Permission : Team member management A maximum of
        20 members can be specified in a single call. If no Dropbox account
        exists with the email address specified, a new Dropbox account will be
        created with the given email address, and that account will be invited
        to the team. If a personal Dropbox account exists with the email address
        specified in the call, this call will create a placeholder Dropbox
        account for the user on the team and send an email inviting the user to
        migrate their existing personal account onto the team. Team member
        management apps are required to set an initial given_name and surname
        for a user to use in the team invitation and for 'Perform as team
        member' actions taken on the user before they become 'active'.

        :param list new_members: Details of new members to be added to the team.
        :param bool force_async: Whether to force the add to happen
            asynchronously.
        :rtype: :class:`dropbox.team.MembersAddLaunch`
        """
        arg = team.MembersAddArg(new_members,
                                 force_async)
        r = self.request(
            'api',
            'team/members/add',
            'rpc',
            bv.Struct(team.MembersAddArg),
            bv.Union(team.MembersAddLaunch),
            bv.Void(),
            arg,
            None,
        )
        return r

    def team_members_add_job_status_get(self,
                                        async_job_id):
        """
        Once an async_job_id is returned from :meth:`members_add` , use this to
        poll the status of the asynchronous request. Permission : Team member
        management

        :param str async_job_id: Id of the asynchronous job. This is the value
            of a response returned from the method that launched the job.
        :rtype: :class:`dropbox.team.MembersAddJobStatus`
        :raises: :class:`dropbox.exceptions.ApiError`

        If this raises, ApiError.reason is of type:
            :class:`dropbox.team.PollError`
        """
        arg = async.PollArg(async_job_id)
        r = self.request(
            'api',
            'team/members/add/job_status/get',
            'rpc',
            bv.Struct(async.PollArg),
            bv.Union(team.MembersAddJobStatus),
            bv.Union(async.PollError),
            arg,
            None,
        )
        return r

    def team_members_get_info(self,
                              members):
        """
        Returns information about multiple team members. Permission : Team
        information This endpoint will return an empty member_info item, for IDs
        (or emails) that cannot be matched to a valid team member.

        :param list members: List of team members.
        :rtype: list
        :raises: :class:`dropbox.exceptions.ApiError`

        If this raises, ApiError.reason is of type:
            :class:`dropbox.team.MembersGetInfoError`
        """
        arg = team.MembersGetInfoArgs(members)
        r = self.request(
            'api',
            'team/members/get_info',
            'rpc',
            bv.Struct(team.MembersGetInfoArgs),
            bv.List(bv.Union(team.MembersGetInfoItem)),
            bv.Union(team.MembersGetInfoError),
            arg,
            None,
        )
        return r

    def team_members_list(self,
                          limit=1000):
        """
        Lists members of a team. Permission : Team information

        :param long limit: Number of results to return per call.
        :rtype: :class:`dropbox.team.MembersListResult`
        :raises: :class:`dropbox.exceptions.ApiError`

        If this raises, ApiError.reason is of type:
            :class:`dropbox.team.MembersListError`
        """
        arg = team.MembersListArg(limit)
        r = self.request(
            'api',
            'team/members/list',
            'rpc',
            bv.Struct(team.MembersListArg),
            bv.Struct(team.MembersListResult),
            bv.Union(team.MembersListError),
            arg,
            None,
        )
        return r

    def team_members_list_continue(self,
                                   cursor):
        """
        Once a cursor has been retrieved from :meth:`members_list`, use this to
        paginate through all team members. Permission : Team information

        :param str cursor: Indicates from what point to get the next set of
            members.
        :rtype: :class:`dropbox.team.MembersListResult`
        :raises: :class:`dropbox.exceptions.ApiError`

        If this raises, ApiError.reason is of type:
            :class:`dropbox.team.MembersListContinueError`
        """
        arg = team.MembersListContinueArg(cursor)
        r = self.request(
            'api',
            'team/members/list/continue',
            'rpc',
            bv.Struct(team.MembersListContinueArg),
            bv.Struct(team.MembersListResult),
            bv.Union(team.MembersListContinueError),
            arg,
            None,
        )
        return r

    def team_members_remove(self,
                            user,
                            wipe_data=True,
                            transfer_dest_id=None,
                            transfer_admin_id=None):
        """
        Removes a member from a team. Permission : Team member management
        Exactly one of team_member_id, email, or external_id must be provided to
        identify the user account. This is not a deactivation where the account
        can be re-activated again. Calling :meth:`members_add` with the removed
        user's email address will create a new account with a new team_member_id
        that will not have access to any content that was shared with the
        initial account. This endpoint can also be used to cancel a pending
        invite to join the team. This endpoint may initiate an asynchronous job.
        To obtain the final result of the job, the client should periodically
        poll :meth:`members_remove_job_status_get`.

        :param Nullable transfer_dest_id: If provided, files from the deleted
            member account will be transferred to this user.
        :param Nullable transfer_admin_id: If provided, errors during the
            transfer process will be sent via email to this user. If the
            transfer_dest_id argument was provided, then this argument must be
            provided as well.
        :rtype: :class:`dropbox.team.LaunchEmptyResult`
        :raises: :class:`dropbox.exceptions.ApiError`

        If this raises, ApiError.reason is of type:
            :class:`dropbox.team.MembersRemoveError`
        """
        arg = team.MembersRemoveArg(user,
                                    wipe_data,
                                    transfer_dest_id,
                                    transfer_admin_id)
        r = self.request(
            'api',
            'team/members/remove',
            'rpc',
            bv.Struct(team.MembersRemoveArg),
            bv.Union(async.LaunchEmptyResult),
            bv.Union(team.MembersRemoveError),
            arg,
            None,
        )
        return r

    def team_members_remove_job_status_get(self,
                                           async_job_id):
        """
        Once an async_job_id is returned from :meth:`members_remove` , use this
        to poll the status of the asynchronous request. Permission : Team member
        management

        :param str async_job_id: Id of the asynchronous job. This is the value
            of a response returned from the method that launched the job.
        :rtype: :class:`dropbox.team.PollEmptyResult`
        :raises: :class:`dropbox.exceptions.ApiError`

        If this raises, ApiError.reason is of type:
            :class:`dropbox.team.PollError`
        """
        arg = async.PollArg(async_job_id)
        r = self.request(
            'api',
            'team/members/remove/job_status/get',
            'rpc',
            bv.Struct(async.PollArg),
            bv.Union(async.PollEmptyResult),
            bv.Union(async.PollError),
            arg,
            None,
        )
        return r

    def team_members_send_welcome_email(self,
                                        arg):
        """
        Sends welcome email to pending team member. Permission : Team member
        management Exactly one of team_member_id, email, or external_id must be
        provided to identify the user account. No-op if team member is not
        pending.

        :param arg: Argument for selecting a single user, either by
            team_member_id, external_id or email.
        :type arg: :class:`dropbox.team.UserSelectorArg`
        :rtype: None
        :raises: :class:`dropbox.exceptions.ApiError`

        If this raises, ApiError.reason is of type:
            :class:`dropbox.team.MembersSendWelcomeError`
        """
        r = self.request(
            'api',
            'team/members/send_welcome_email',
            'rpc',
            bv.Union(team.UserSelectorArg),
            bv.Void(),
            bv.Union(team.MembersSendWelcomeError),
            arg,
            None,
        )
        return None

    def team_members_set_admin_permissions(self,
                                           user,
                                           new_role):
        """
        Updates a team member's permissions. Permission : Team member management

        :param user: Identity of user whose role will be set.
        :type user: :class:`dropbox.team.UserSelectorArg`
        :param new_role: The new role of the member.
        :type new_role: :class:`dropbox.team.AdminTier`
        :rtype: :class:`dropbox.team.MembersSetPermissionsResult`
        :raises: :class:`dropbox.exceptions.ApiError`

        If this raises, ApiError.reason is of type:
            :class:`dropbox.team.MembersSetPermissionsError`
        """
        arg = team.MembersSetPermissionsArg(user,
                                            new_role)
        r = self.request(
            'api',
            'team/members/set_admin_permissions',
            'rpc',
            bv.Struct(team.MembersSetPermissionsArg),
            bv.Struct(team.MembersSetPermissionsResult),
            bv.Union(team.MembersSetPermissionsError),
            arg,
            None,
        )
        return r

    def team_members_set_profile(self,
                                 user,
                                 new_email=None,
                                 new_external_id=None,
                                 new_given_name=None,
                                 new_surname=None):
        """
        Updates a team member's profile. Permission : Team member management

        :param user: Identity of user whose profile will be set.
        :type user: :class:`dropbox.team.UserSelectorArg`
        :param Nullable new_email: New email for member.
        :param Nullable new_external_id: New external ID for member.
        :param Nullable new_given_name: New given name for member.
        :param Nullable new_surname: New surname for member.
        :rtype: :class:`dropbox.team.TeamMemberInfo`
        :raises: :class:`dropbox.exceptions.ApiError`

        If this raises, ApiError.reason is of type:
            :class:`dropbox.team.MembersSetProfileError`
        """
        arg = team.MembersSetProfileArg(user,
                                        new_email,
                                        new_external_id,
                                        new_given_name,
                                        new_surname)
        r = self.request(
            'api',
            'team/members/set_profile',
            'rpc',
            bv.Struct(team.MembersSetProfileArg),
            bv.Struct(team.TeamMemberInfo),
            bv.Union(team.MembersSetProfileError),
            arg,
            None,
        )
        return r

    def team_members_suspend(self,
                             user,
                             wipe_data=True):
        """
        Suspend a member from a team. Permission : Team member management
        Exactly one of team_member_id, email, or external_id must be provided to
        identify the user account.

        :param user: Identity of user to remove/suspend.
        :type user: :class:`dropbox.team.UserSelectorArg`
        :param bool wipe_data: If provided, controls if the user's data will be
            deleted on their linked devices.
        :rtype: None
        :raises: :class:`dropbox.exceptions.ApiError`

        If this raises, ApiError.reason is of type:
            :class:`dropbox.team.MembersSuspendError`
        """
        arg = team.MembersDeactivateArg(user,
                                        wipe_data)
        r = self.request(
            'api',
            'team/members/suspend',
            'rpc',
            bv.Struct(team.MembersDeactivateArg),
            bv.Void(),
            bv.Union(team.MembersSuspendError),
            arg,
            None,
        )
        return None

    def team_members_unsuspend(self,
                               user):
        """
        Unsuspend a member from a team. Permission : Team member management
        Exactly one of team_member_id, email, or external_id must be provided to
        identify the user account.

        :param user: Identity of user to unsuspend.
        :type user: :class:`dropbox.team.UserSelectorArg`
        :rtype: None
        :raises: :class:`dropbox.exceptions.ApiError`

        If this raises, ApiError.reason is of type:
            :class:`dropbox.team.MembersUnsuspendError`
        """
        arg = team.MembersUnsuspendArg(user)
        r = self.request(
            'api',
            'team/members/unsuspend',
            'rpc',
            bv.Struct(team.MembersUnsuspendArg),
            bv.Void(),
            bv.Union(team.MembersUnsuspendError),
            arg,
            None,
        )
        return None

    def team_reports_get_activity(self,
                                  start_date=None,
                                  end_date=None):
        """
        Retrieves reporting data about a team's user activity.

        :param Nullable start_date: Optional starting date (inclusive)
        :param Nullable end_date: Optional ending date (exclusive)
        :rtype: :class:`dropbox.team.GetActivityReport`
        :raises: :class:`dropbox.exceptions.ApiError`

        If this raises, ApiError.reason is of type:
            :class:`dropbox.team.DateRangeError`
        """
        arg = team.DateRange(start_date,
                             end_date)
        r = self.request(
            'api',
            'team/reports/get_activity',
            'rpc',
            bv.Struct(team.DateRange),
            bv.Struct(team.GetActivityReport),
            bv.Union(team.DateRangeError),
            arg,
            None,
        )
        return r

    def team_reports_get_devices(self,
                                 start_date=None,
                                 end_date=None):
        """
        Retrieves reporting data about a team's linked devices.

        :param Nullable start_date: Optional starting date (inclusive)
        :param Nullable end_date: Optional ending date (exclusive)
        :rtype: :class:`dropbox.team.GetDevicesReport`
        :raises: :class:`dropbox.exceptions.ApiError`

        If this raises, ApiError.reason is of type:
            :class:`dropbox.team.DateRangeError`
        """
        arg = team.DateRange(start_date,
                             end_date)
        r = self.request(
            'api',
            'team/reports/get_devices',
            'rpc',
            bv.Struct(team.DateRange),
            bv.Struct(team.GetDevicesReport),
            bv.Union(team.DateRangeError),
            arg,
            None,
        )
        return r

    def team_reports_get_membership(self,
                                    start_date=None,
                                    end_date=None):
        """
        Retrieves reporting data about a team's membership.

        :param Nullable start_date: Optional starting date (inclusive)
        :param Nullable end_date: Optional ending date (exclusive)
        :rtype: :class:`dropbox.team.GetMembershipReport`
        :raises: :class:`dropbox.exceptions.ApiError`

        If this raises, ApiError.reason is of type:
            :class:`dropbox.team.DateRangeError`
        """
        arg = team.DateRange(start_date,
                             end_date)
        r = self.request(
            'api',
            'team/reports/get_membership',
            'rpc',
            bv.Struct(team.DateRange),
            bv.Struct(team.GetMembershipReport),
            bv.Union(team.DateRangeError),
            arg,
            None,
        )
        return r

    def team_reports_get_storage(self,
                                 start_date=None,
                                 end_date=None):
        """
        Retrieves reporting data about a team's storage usage.

        :param Nullable start_date: Optional starting date (inclusive)
        :param Nullable end_date: Optional ending date (exclusive)
        :rtype: :class:`dropbox.team.GetStorageReport`
        :raises: :class:`dropbox.exceptions.ApiError`

        If this raises, ApiError.reason is of type:
            :class:`dropbox.team.DateRangeError`
        """
        arg = team.DateRange(start_date,
                             end_date)
        r = self.request(
            'api',
            'team/reports/get_storage',
            'rpc',
            bv.Struct(team.DateRange),
            bv.Struct(team.GetStorageReport),
            bv.Union(team.DateRangeError),
            arg,
            None,
        )
        return r

