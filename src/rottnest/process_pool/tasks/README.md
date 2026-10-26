# Pool Tasks

This is a double sided interface for `process_pool`
and `pool_manager`.

Objects inherit `PoolTask`, which implements a collector pattern. And are bound in the `__init__`

Return values from tasks are then passed back over the socket to the IPC manager.

## `EXPECT_RESPONSE`
Class variable, if set then the task is expected to return a not None value.
Should be set to a boolean value

## `get_command`
Returns a task name string for submission by the `process_pool`, and to be bound to the task vtable in `pool_manager`

## `get_poll_key`
Covers cases where the polling IPC key differs from the command key. Defaults to the command key. 

## `get_finalise_key`
Covers cases wher the finalise key differs from the command key. Defaults to the command key.

## `__call__`
Dispatches to task, this uses a wrapped `expect_response` handler. Directly calling `task` skips the handler.
This wraps the `pool_manager` side call.

## `setup`
API side setup as a classmethod, as the 

## `submit`
Wrapper for the `process_pool` side call

## `task`
Internal method called by the `pool_manager`.
