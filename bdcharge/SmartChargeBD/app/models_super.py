from app import models


class SDevopsTaskInfoSuper(models.SDevopsTaskInfo):
    # 任务描述
    def get_task_desc(self):
        site = models.SSiteInfo.objects.filter(site_id=self.site_id).first()
        return {
            "task_id": self.id,
            "task_name": self.task_name,
            "site_name": site.site_name if site else "-",
            'state': self.state,
            "eq_id": self.eq_id if self.eq_id else "--",
        }

    @property
    def site_name(self):
        site = models.SSiteInfo.objects.filter(site_id=self.site_id).first()
        if site:
            return site.site_name
        return '-'

    @property
    def site_address(self):
        site = models.SSiteInfo.objects.filter(site_id=self.site_id).first()
        if site:
            return site.site_address
        return '-'

    class Meta:
        # 代理模式 https://www.liujiangblog.com/course/django/100
        proxy = True

