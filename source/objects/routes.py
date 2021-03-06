from base.database import db, get_obj
from base.helpers import allowed_file
from base.properties import (
    pretty_names,
    link_public_properties,
    node_public_properties
)
from flask import Blueprint, jsonify, render_template, request
from flask_login import login_required
from .forms import AddNode, AddLink, FilteringForm
from .models import filter_factory, Filter, Link, Node, object_class, object_factory
from werkzeug.utils import secure_filename
from xlrd import open_workbook
from xlrd.biffh import XLRDError

blueprint = Blueprint(
    'objects_blueprint',
    __name__,
    url_prefix='/objects',
    template_folder='templates',
    static_folder='static'
)

## Template rendering


@blueprint.route('/object_management', methods=['GET', 'POST'])
@login_required
def objects():
    add_node_form = AddNode(request.form)
    add_link_form = AddLink(request.form)
    all_nodes = Node.choices()
    add_link_form.source.choices = add_link_form.destination.choices = all_nodes
    if request.method == 'POST':
        file = request.files['file']
        if allowed_file(secure_filename(file.filename), {'xls', 'xlsx'}):
            book = open_workbook(file_contents=file.read())
            for obj_type, cls in object_class.items():
                try:
                    sheet = book.sheet_by_name(obj_type)
                # if the sheet cannot be found, there's nothing to import
                except XLRDError:
                    continue
                properties = sheet.row_values(0)
                for row_index in range(1, sheet.nrows):
                    kwargs = dict(zip(properties, sheet.row_values(row_index)))
                    kwargs['type'] = obj_type
                    object_factory(**kwargs)
                db.session.commit()
    return render_template(
        'object_management.html',
        names=pretty_names,
        node_fields=node_public_properties,
        nodes=Node.visible_objects(),
        link_fields=link_public_properties,
        links=Link.visible_objects(),
        add_node_form=add_node_form,
        add_link_form=add_link_form
    )


@blueprint.route('/object_filtering')
@login_required
def filter_objects():
    return render_template(
        'object_filtering.html',
        form=FilteringForm(request.form),
        names=pretty_names,
        filters=[f.name for f in Filter.query.all()]
    )


## AJAX calls


@blueprint.route('/get/<obj_type>/<name>', methods=['POST'])
@login_required
def get_object(obj_type, name):
    cls = Node if obj_type == 'node' else Link
    properties = node_public_properties if cls == Node else link_public_properties
    obj = get_obj(cls, name=name)
    obj_properties = {
        property: str(getattr(obj, property))
        for property in properties
    }
    return jsonify(obj_properties)


@blueprint.route('/edit_object', methods=['GET', 'POST'])
@login_required
def edit_object():
    object_factory(**request.form.to_dict())
    db.session.commit()
    return jsonify({})


@blueprint.route('/delete/<obj_type>/<name>', methods=['POST'])
@login_required
def delete_object(obj_type, name):
    cls = Node if obj_type == 'node' else Link
    obj = get_obj(cls, name=name)
    db.session.delete(obj)
    db.session.commit()
    return jsonify({})


@blueprint.route('/process_filter', methods=['POST'])
@login_required
def process_filter():
    filter_properties = request.form.to_dict()
    for property in node_public_properties:
        regex_property = 'node_{}_regex'.format(property)
        filter_properties[regex_property] = regex_property in filter_properties
    for property in link_public_properties:
        regex_property = 'link_{}_regex'.format(property)
        filter_properties[regex_property] = regex_property in filter_properties
    mode = filter_factory(**filter_properties)
    return jsonify(mode)


@blueprint.route('/get/<name>', methods=['POST'])
@login_required
def get_filter(name):
    return jsonify(get_obj(Filter, name=name).get_properties())


@blueprint.route('/<name>/filter_objects', methods=['POST'])
@login_required
def get_filtered_objects(name):
    filter = get_obj(Filter, name=name)
    objects = filter.filter_objects()
    return jsonify(objects)
