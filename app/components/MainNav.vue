<script lang="ts" setup>
import { ChevronDown, Menu, ListIndentDecrease } from "@lucide/vue";
import { navigationMenuTriggerStyle } from "~/components/ui/navigation-menu";
import { navigation } from "~/utils/consts";
import { cn } from "~/lib/utils";

const router = useRouter();
const route = useRoute();

const props = defineProps<{
	allowToggleNav?: boolean;
}>();

const linkClasses = "bg-transparent hover:bg-black/10 transition-colors";

const showSidenav = ref(false);
const expandNav = ref(route.path !== "/");

router.beforeEach((from, to) => {
	showSidenav.value = false;
	expandNav.value = false;
});
</script>

<template>
	<!--		    mobile nav-->
	<Sheet v-model:open="showSidenav">
		<SheetTrigger asChild>
			<Button variant="ghost" size="icon" class="md:hidden bg-transparent hover:bg-black/10 transition-colors"><Menu /></Button>
		</SheetTrigger>
		<SheetContent size="right" class="p-3">
			<a href="https://indigenousdatacommons.org" class="mr-auto">
				<NuxtImg src="/img/idc-logo.png" class="w-48 h-auto" />
			</a>
			<div class="flex flex-col gap-2 overflow-y-auto">
				<div v-for="link of navigation">
					<Collapsible v-if="!!link.children && link.children.length > 1" :defaultOpen="link.active || route.path.startsWith(link.path)">
						<CollapsibleTrigger asChild>
							<Button variant="ghost" :class="`text-sm font-medium bg-transparent hover:bg-black/10 transition-colors w-full data-active:!text-isu-red justify-between ${route.path.startsWith(link.path) ? '!text-isu-red' : ''}`">
								{{link.title}}
								<ChevronDown :class="`size-4`" />
							</Button>
						</CollapsibleTrigger>
						<CollapsibleContent>
							<div class="dark bg-secondary text-secondary-foreground p-2 gap-2 flex flex-col rounded-lg">
								<Button variant="ghost" v-for="child in link.children.filter(c => c.path !== link.path)" :data-active="child.active || route.path === child.path || undefined" class="nav-link hover:!bg-background/30 transition-colors data-active:bg-background/50 hover:data-active:bg-background/50 justify-start text-ellipsis overflow-hidden" asChild>
									<NuxtLink :to="child.path">
										<div class="leading-none font-medium text-sm">
											{{ child.title }}
										</div>
									</NuxtLink>
								</Button>
							</div>
						</CollapsibleContent>
					</Collapsible>
					<Button variant="ghost" v-else :class="`bg-transparent hover:bg-black/10 transition-colors data-active:!text-isu-red w-full justify-start ${link.active || route.path === link.path ? '!text-isu-red' : ''}`" asChild>
						<NuxtLink :to="link.path">{{link.title}}</NuxtLink>
					</Button>
				</div>
			</div>
		</SheetContent>
	</Sheet>
	<div :class="props.allowToggleNav ? `transition-opacity ${expandNav ? '' : 'opacity-0'}` : ''">
		<!--		    desktop nav-->
		<NavigationMenu v-show="!props.allowToggleNav || expandNav" class="max-md:hidden **:data-[slot=navigation-menu-viewport]:bg-secondary **:data-[slot=navigation-menu-viewport]:border-none">
			<NavigationMenuList>
				<NavigationMenuItem v-for="link of navigation">
					<template v-if="!!link.children && link.children.length > 1">
						<NavigationMenuTrigger :class="cn(linkClasses, 'data-[state=open]:hover:bg-black/20', link.active || route.path.startsWith(link.path) ? '!text-isu-red' : '')">{{link.title}}</NavigationMenuTrigger>
						<NavigationMenuContent class="dark bg-secondary text-secondary-foreground p-4 gap-4 grid sm:grid-cols-2 md:grid-cols-4 lg:grid-cols-5 !w-[calc(100dvw-35px)] rounded-lg">
							<NavigationMenuLink v-for="child in link.children.filter(c => c.path !== link.path)" :active="child.active || route.path === child.path" class="nav-link hover:not-data-active:bg-background/30 transition-colors p-4 rounded-md data-active:bg-background/50 hover:data-active:bg-background/50" asChild>
								<NuxtLink :to="child.path">
									<div class="leading-none font-medium text-base">
										{{ child.title }}
									</div>
									<p v-if="child.description" class="text-sm line-clamp-3 leading-snug text-muted-foreground">
										{{ child.description }}
									</p>
								</NuxtLink>
							</NavigationMenuLink>
						</NavigationMenuContent>
					</template>
					<NavigationMenuLink v-else :active="link.active || route.path === link.path" :class="cn(navigationMenuTriggerStyle(), 'bg-transparent hover:bg-black/10 transition-colors data-active:!text-isu-red')" asChild>
						<NuxtLink :to="link.path">{{link.title}}</NuxtLink>
					</NavigationMenuLink>
				</NavigationMenuItem>
			</NavigationMenuList>
		</NavigationMenu>
	</div>
	<Button v-if="props.allowToggleNav" size="icon" variant="ghost" :class="`max-md:hidden ${linkClasses}`" title="Toggle navbar" @click="expandNav = !expandNav">
		<ListIndentDecrease :class="`size-4 transition-transform ${expandNav ? 'rotate-y-180' : ''}`" />
	</Button>
</template>

<style scoped>
.nav-link {
	--active-color: hsl(4.55 65% 55%);
	&[data-active] {
		color: var(--active-color);
	}
}
</style>