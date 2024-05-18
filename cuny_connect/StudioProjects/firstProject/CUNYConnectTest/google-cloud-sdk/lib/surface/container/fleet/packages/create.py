# -*- coding: utf-8 -*- #
# Copyright 2024 Google LLC. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Command to create Fleet Package."""

from googlecloudsdk.api_lib.container.fleet.packages import fleet_packages as apis
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.container.fleet.packages import flags
from googlecloudsdk.command_lib.container.fleet.packages import utils as command_utils
from googlecloudsdk.command_lib.export import util as export_util
from googlecloudsdk.core.console import console_io


_DETAILED_HELP = {
    'DESCRIPTION': '{description}',
    'EXAMPLES': """ \
        To create Fleet Package ``cert-manager-app'', run:

          $ {command} cert-manager-app --source=source.yaml
        """,
}


@base.Hidden
@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
class Create(base.CreateCommand):
  """Create Package Rollouts Fleet Package."""

  detailed_help = _DETAILED_HELP

  @staticmethod
  def Args(parser):
    flags.AddSourceFlag(parser)
    flags.AddNameFlag(parser)
    flags.AddLocationFlag(parser)

  def Run(self, args):
    """Run the create command."""
    client = apis.FleetPackagesClient()
    data = console_io.ReadFromFileOrStdin(args.source, binary=False)
    fleet_package = export_util.Import(
        message_type=client.messages.FleetPackage,
        stream=data,
    )
    if not fleet_package.variantSelector:
      fleet_package.variantSelector = client.messages.VariantSelector(
          variantNameTemplate='default'
      )

    fleet_package = command_utils.UpsertDefaultVariants(fleet_package)

    parent = (
        f'projects/{flags.GetProject(args)}/locations/{flags.GetLocation(args)}'
    )

    return client.Create(
        fleet_package=fleet_package, fleet_package_id=args.name, parent=parent
    )
