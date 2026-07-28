"""Device-level availability tracking for Treeow cloud devices."""

from typing import Any, Mapping, Optional


DEVICE_STATUS_ONLINE = 1
DEVICE_STATUS_OFFLINE = 2
DEFAULT_POLL_FAILURE_LIMIT = 3


def decode_device_availability(payload: Mapping[str, Any]) -> Optional[bool]:
    """Decode Treeow's device status without guessing unknown values."""
    status = payload.get("status")
    if isinstance(status, bool):
        return None

    try:
        status = int(status)
    except (TypeError, ValueError):
        return None

    if status == DEVICE_STATUS_ONLINE:
        return True
    if status == DEVICE_STATUS_OFFLINE:
        return False
    return None


class DeviceAvailabilityTracker:
    """Track explicit cloud status and bounded transport failures."""

    __slots__ = ("_available", "_consecutive_failures", "_failure_limit")

    def __init__(
        self,
        initial_payload: Optional[Mapping[str, Any]] = None,
        *,
        failure_limit: int = DEFAULT_POLL_FAILURE_LIMIT,
    ) -> None:
        if failure_limit < 1:
            raise ValueError("failure_limit must be at least 1")

        self._available = False
        self._consecutive_failures = 0
        self._failure_limit = failure_limit

        if initial_payload is not None:
            initial_available = decode_device_availability(initial_payload)
            if initial_available is not None:
                self._available = initial_available

    @property
    def available(self) -> bool:
        """Return the last confirmed device availability."""
        return self._available

    @property
    def consecutive_failures(self) -> int:
        """Return the number of consecutive failed device polls."""
        return self._consecutive_failures

    def observe_payload(self, payload: Mapping[str, Any]) -> bool:
        """Apply a successful API payload and report an availability change."""
        self._consecutive_failures = 0
        available = decode_device_availability(payload)
        if available is None or available == self._available:
            return False

        self._available = available
        return True

    def observe_failure(self) -> bool:
        """Mark unavailable after the configured consecutive failure limit."""
        self._consecutive_failures += 1
        if (
            self._consecutive_failures < self._failure_limit
            or not self._available
        ):
            return False

        self._available = False
        return True

    def force_unavailable(self) -> bool:
        """Force an unavailable state and report whether it changed."""
        self._consecutive_failures = max(
            self._consecutive_failures,
            self._failure_limit,
        )
        if not self._available:
            return False

        self._available = False
        return True
