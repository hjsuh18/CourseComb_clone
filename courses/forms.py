from django import forms

class Filter(forms.Form):
	# distributions
	ha = forms.BooleanField(label="HA", required=False)
	sa = forms.BooleanField(label="SA", required=False)
	stl = forms.BooleanField(label="STL", required=False)
	stn = forms.BooleanField(label="STN", required=False)
	ec = forms.BooleanField(label="EC", required=False)
	em = forms.BooleanField(label="EM", required=False)
	la = forms.BooleanField(label="LA", required=False)
	qr = forms.BooleanField(label="QR", required=False)

	# maximum number of departmentals
	max_dept = forms.IntegerField(label="Maximum # of Courses is one department", min_value=1, max_value=5, required=False)

	# time of class
	no_friday_class = forms.BooleanField(label="No Friday Class", required=False)
	no_evening_class = forms.BooleanField(label="No Evenig Class", required=False)
	after_ten_am = forms.BooleanField(label="After 10am", required=False)

	# Exclude fully enrolled classes
	full = forms.BooleanField(label="Exclude fully enrolled classes", required=False)

	# Include 1 PDF-only Class
	pdf = forms.BooleanField(label="PDF", required=False)