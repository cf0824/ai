from django.db import models
# .

class ViewUserAccountOk(models.Model):
    id = models.BigIntegerField(primary_key=True)
    user_id = models.IntegerField()
    real_money = models.DecimalField(max_digits=12, decimal_places=2)
    ice_money = models.DecimalField(max_digits=34, decimal_places=2)
    ok_money = models.DecimalField(max_digits=35, decimal_places=2)
    gift_money = models.DecimalField(max_digits=35, decimal_places=2)
    gift_ice = models.DecimalField(max_digits=35, decimal_places=2)

    class Meta:
        managed = False  # Created from a view. Don't remove.
        db_table = 'view_user_account_ok'
