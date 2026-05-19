from app.models import SSiteDevopsUser


# 查询有权限的站点
def get_auth_site_ids(dev_user_id):
    site_ids = SSiteDevopsUser.objects.filter(dev_user_id=dev_user_id).values_list('site_id', flat=True)
    return site_ids
