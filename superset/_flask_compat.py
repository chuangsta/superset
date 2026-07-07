# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
"""Compatibility shim for Flask 3.x with Flask-SQLAlchemy 2.5.x.

Flask 3.0 removed ``flask._app_ctx_stack`` (a Werkzeug ``LocalStack``).
Flask-SQLAlchemy 2.5.x imports it at module level to store per-request
query recordings.  Upgrading Flask-SQLAlchemy to 3.x is blocked because
it requires SQLAlchemy >= 2.0, while Superset pins SQLAlchemy < 2.

This module re-exposes a lightweight shim on ``flask._app_ctx_stack`` so
that Flask-SQLAlchemy 2.5.x can be imported under Flask 3.x.  The shim
delegates attribute storage to ``flask.g``, which is the canonical
per-app-context namespace in Flask 3.x.

Import this module before any code that transitively imports
``flask_sqlalchemy``.
"""

import flask
from flask.globals import _cv_app


class _GProxy:
    """Proxy that reads/writes attributes on ``flask.g``."""

    __slots__ = ()

    def __getattr__(self, name: str) -> object:
        return getattr(flask.g, name)

    def __setattr__(self, name: str, value: object) -> None:
        setattr(flask.g, name, value)


class _AppCtxStackShim:
    """Minimal stand-in for the removed ``flask._app_ctx_stack``."""

    __slots__ = ()

    @property
    def top(self) -> "_GProxy | None":
        if _cv_app.get(None) is None:
            return None
        return _GProxy()


if not hasattr(flask, "_app_ctx_stack"):
    flask._app_ctx_stack = _AppCtxStackShim()
