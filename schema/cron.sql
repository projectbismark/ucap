UPDATE household_caps_curr set startdt = enddt, enddt = enddt + interval '1 month', usage = 0 where date(enddt) - date(localtimestamp) < 0;
UPDATE user_caps_curr set startdt = enddt, enddt = enddt + interval '1 month', usage = 0 where date(enddt) - date(localtimestamp) < 0;
UPDATE device_caps_curr set startdt = enddt, enddt = enddt + interval '1 month', usage = -1 where date(enddt) - date(localtimestamp) < 0;
