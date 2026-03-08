from django.contrib import admin

from .models import BagDisc, Collection, Disc


class DiscInline(admin.TabularInline):
    model = Disc
    extra = 0
    fields = ('name', 'manufacturer', 'plastic', 'weight', 'color', 'acquired_at')
    ordering = ('-acquired_at',)


class BagDiscInline(admin.TabularInline):
    model = BagDisc
    extra = 0
    fields = ('disc', 'added_at')
    readonly_fields = ('added_at',)
    autocomplete_fields = ('disc',)
    ordering = ('-added_at',)


@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at', 'disc_count', 'bag_disc_count')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('created_at',)
    inlines = (DiscInline, BagDiscInline)

    @admin.display(description='Discs')
    def disc_count(self, obj):
        return obj.discs.count()

    @admin.display(description='In My Bag')
    def bag_disc_count(self, obj):
        return obj.bag_discs.count()


@admin.register(Disc)
class DiscAdmin(admin.ModelAdmin):
    list_display = ('name', 'manufacturer', 'plastic', 'weight', 'color', 'acquired_at', 'collection')
    list_filter = ('manufacturer', 'plastic', 'color')
    search_fields = ('name', 'manufacturer', 'plastic', 'collection__user__username')
    autocomplete_fields = ('collection',)
    ordering = ('-acquired_at', 'name')


@admin.register(BagDisc)
class BagDiscAdmin(admin.ModelAdmin):
    list_display = ('disc', 'collection', 'user', 'added_at')
    list_filter = ('added_at',)
    search_fields = ('disc__name', 'collection__user__username')
    autocomplete_fields = ('collection', 'disc')
    ordering = ('-added_at',)

    @admin.display(description='User')
    def user(self, obj):
        return obj.collection.user