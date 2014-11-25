#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
"""Empty migration just to get us started may need to be removed when we have
some proper one in the future.

Revision ID: 3b0f6711681
Revises: 4f57a800218
Create Date: 2014-11-17 11:40:47.579747

"""

# revision identifiers, used by Alembic.
revision = '3b0f6711681'
down_revision = None

from alembic import op  # noqa
import sqlalchemy as sa  # noqa


def upgrade():
    pass


def downgrade():
    pass
