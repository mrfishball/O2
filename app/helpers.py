from flask import render_template, request
from flask.ext.restless import ProcessingException
from posts.forms import CommentForm
import random

# This function create a paginated list of objects of the requested type.
def object_list(template_name, query, paginate_by=5, **context):
	page = request.args.get('page')
	if page and page.isdigit():
		page = int(page)
	else:
		page = 1
	object_list = query.paginate(page, paginate_by)
	return render_template(template_name, object_list=object_list, **context)

# Accept deserialized POST data as arguement and pass it to the CommentForm object for validation.
def post_preprocessor(data, **kwargs):
	form = CommentForm(data=data)
	if form.validate():
		return form.data
	else:
		raise ProcessingException(
			description='Invalid form submission.', code=400)