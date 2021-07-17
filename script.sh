#!/bin/bash
mysql -u vesta -pFardis_parvaz123
<<EOF
USE vestabot;
UPDATE sepehr_supplier SET status=False WHERE status=True;
UPDATE ravis_supplier SET status=False WHERE status=True;
exit
<<EOF
