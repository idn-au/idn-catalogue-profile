<script lang="ts" setup>
import { Sun, Moon, SunMoon, Hammer } from "@lucide/vue";

const router = useRouter();
const route = useRoute();
const colorMode = useColorMode();

const props = defineProps<{
	allowToggleNav?: boolean;
}>();

const linkClasses = "bg-transparent hover:bg-black/10 transition-colors";

const showSidenav = ref(false);
const expandNav = ref(route.path !== "/");
// const expandNav = ref(true);

router.beforeEach((from, to) => {
	showSidenav.value = false;
	expandNav.value = false;
});
</script>

<template>
	<header :class="`top-nav sticky top-0 flex flex-row items-center p-4 gap-2 z-49 transition-colors flex-wrap ${props.allowToggleNav ? 'bg-transparent' : 'bg-background'}`">
<!--		<Alert class="w-full border-none bg-transparent p-0 text-muted-foreground text-sm">-->
<!--			<Hammer />-->
<!--			<AlertTitle>This website is currently under development</AlertTitle>-->
<!--		</Alert>-->
		<a href="https://indigenousdatacommons.org" class="mr-auto">
			<NuxtImg src="/img/idc-logo.png" class="w-50 md:w-62 h-auto" />
		</a>
		<MainNav :allowToggleNav="props.allowToggleNav" />
<!--		<SearchCommand icon :class="linkClasses" />-->
        <Button variant="ghost" size="icon" @click="!colorMode.unknown ? colorMode.value === 'dark' ? colorMode.preference = 'light' : colorMode.preference = 'dark' : undefined">
	        <SunMoon v-show="colorMode.unknown" />
	        <Sun v-show="colorMode.value === 'dark'" class="size-4" />
	        <Moon v-show="colorMode.value === 'light'" class="size-4" />
        </Button>
	</header>
</template>
