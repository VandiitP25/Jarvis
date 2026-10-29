
from winotify import Notification

toast = Notification(
    app_id="JARVIS",
    title="JARVIS",
    msg="Background notifications are working!",
    duration="short",
)

toast.show()
print("Notification test sent.")
