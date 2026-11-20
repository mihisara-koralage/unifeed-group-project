from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods, require_safe

from .forms import ResourceForm
from .models import Resource
from .validators import validate_resource_url


@login_required
@require_safe
def resource_list(request):
    category = request.GET.get('category', '')
    search = request.GET.get('search', '').strip()
    resources = Resource.objects.filter(is_approved=True).select_related('contributor')
    if category in Resource.Category.values:
        resources = resources.filter(category=category)
    else:
        category = ''
    if search:
        resources = resources.filter(Q(title__icontains=search) | Q(description__icontains=search))
    return render(request, 'resources/list.html', {
        'resources': resources,
        'categories': Resource.Category.choices,
        'active_cat': category,
        'search': search,
    })


@login_required
@require_http_methods(['GET', 'POST'])
def submit_resource(request):
    if not request.user.is_student:
        messages.error(request, 'Only students can submit resources.')
        return redirect('resources:list')
    form = ResourceForm(request.POST if request.method == 'POST' else None)
    if request.method == 'POST' and form.is_valid():
        resource = form.save(commit=False)
        resource.contributor = request.user
        resource.save()
        messages.success(request, 'Resource submitted successfully!')
        return redirect('resources:list')
    return render(request, 'resources/submit.html', {'form': form})


@login_required
@require_safe
def open_resource(request, resource_id):
    resource = get_object_or_404(Resource, pk=resource_id, is_approved=True)
    # Guard the preview even for legacy records saved without model validation.
    try:
        validate_resource_url(resource.url)
    except ValidationError:
        raise Http404('This resource link is not available.')
    return render(request, 'resources/redirect.html', {'resource': resource})
