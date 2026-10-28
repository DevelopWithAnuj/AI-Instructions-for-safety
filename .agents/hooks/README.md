# Shared hooks

This directory is the home for reusable hook implementations. Keep hook logic here so it can be reused by multiple AI tools.

## Tool adapters

Hook systems are not universal. Each tool may use different configuration files, event names, input/output contracts, and supported lifecycle events. A script in this directory is not active until a tool-specific adapter calls it.

When adding a hook:

1. Agree on the behavior and lifecycle event first.
2. Implement the reusable logic in this directory.
3. Add a minimal native adapter for each tool that supports the required event.
4. Test the behavior in every configured tool and document any unsupported tools or events.

No hook behavior or tool adapters are currently enabled. Add adapters only after their behavior is defined.
