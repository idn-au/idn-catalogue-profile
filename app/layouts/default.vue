<script lang="ts" setup>
import { Newspaper } from "@lucide/vue";
import {FontAwesomeIcon} from "@fortawesome/vue-fontawesome";
import {faFacebookF, faInstagram, faLinkedinIn, faYoutube, type IconDefinition, faXTwitter} from "@fortawesome/free-brands-svg-icons";

const socials: {
	title: string;
	icon: IconDefinition,
	url: string;
}[] = [
	{
		title: "Facebook",
		icon: faFacebookF,
		url: "https://www.facebook.com/ISU.UniMelb",
	},
	{
		title: "Instagram",
		icon: faInstagram,
		url: "https://www.instagram.com/isu.unimelb/",
	},
	{
		title: "LinkedIn",
		icon: faLinkedinIn,
		url: "https://www.linkedin.com/company/indigenous-data-network/posts/?feedView=all",
	},
	{
		title: "YouTube",
		icon: faYoutube,
		url: "https://www.youtube.com/@IndigenousStudiesUnit",
	},
	{
		title: "X",
		icon: faXTwitter,
		url: "https://x.com/indigenousUoM",
	},
];

const defaultImage = "/img/Milky_Way_IDN_Logo_75percent-fpng.webp";
</script>

<template>
	<div class="min-h-dvh flex flex-col">
		<IDCHeader />
		<div class="mx-auto max-w-[1400px] w-full">
			<AppNav />
		</div>
		<main class="grow mb-12">
			<div class="min-h-[300px] py-0 px-2 flex flex-col justify-end bg-cover bg-no-repeat bg-center relative -z-1 isolate mb-6" :style="{backgroundImage: `url(${defaultImage})`}">
				<div class="mx-auto max-w-[1400px] w-full">
					<h1 class="text-white text-5xl mt-6 mb-10.5"><slot name="title" /></h1>
					<p class="text-white font-bold my-5"><slot name="description" /></p>
				</div>
				<IDCLogo class="fill-isu-yellow absolute h-[750px] w-auto -top-[50px] right-0 opacity-30 dark:opacity-10 saturate-10 brightness-140 -z-1" />
			</div>
			<div class="mx-auto px-2 max-w-[1400px] prose dark:prose-invert">
				<slot />
			</div>
		</main>
		<div class="bg-isu-yellow/10 py-12 relative overflow-hidden isolate">
			<!--			<NuxtImg src="/img/symbol/UoM_Indig.Data.Com_Brand_Art_RGB_Symbol_Red.svg" class="absolute h-[1000%] -z-1 opacity-20 -left-[37%] top-[45%] rotate-3 -translate-y-1/2" />-->
			<IDCLogo class="h-[700px] w-auto absolute opacity-20 fill-isu-red rotate-3 -translate-y-1/2 -left-[240px] -z-1" />
			<div class="mx-auto max-w-[1200px] text-center">
				The Indigenous Data Network acknowledges the Aboriginal and Torres Strait Islander Traditional Custodians of the lands on which we work and live. We pay respect to their Elders, past and present, and the place of Indigenous Knowledge in the academy and beyond. We acknowledge and respect that Aboriginal and Torres Strait Islander people have always used resources from the land and waters for nourishment, medicine and healing.
			</div>
		</div>

		<div class="bg-secondary">
			<div class="mx-auto max-w-[1200px] py-12 px-5 text-center flex flex-col items-center gap-6">
				<div class="flex flex-col md:flex-row md:flex-wrap items-center justify-center gap-8 mx-auto">
					<img src="/img/idn-logo-250.png" alt="IDN Logo" class="h-[80px]" />
					<img src="/img/logo-um.svg" alt="UoM Logo" class="w-[80px]" />
					<img src="/img/ARDC-logo.png" alt="ARDC Logo" class="w-[200px] lg:hidden" />
					<img src="/img/NCRIS-PROVIDER.png" alt="NCRIS Logo" class="h-[100px] lg:hidden" />
					<img src="/img/ARDC-AUS-NCRIS-logo.png" alt="ARDC, Australian Government and NCRIS Logos" class="h-[100px] hidden lg:flex" />
				</div>

				<div class="text-sm">
					Improving Indigenous Research Capabilities is a co-investment partnership with the Australian Research Data Commons (ARDC) through the HASS and Indigenous Research Data Commons (DOI: <a href="https://doi.org/10.3565/pr3g-s109" target="_blank"> 10.3565/pr3g-s109 </a>). The ARDC is enabled by the Australian Government’s National Collaborative Research Infrastructure Strategy (NCRIS).
				</div>
			</div>
		</div>

		<footer class="dark bg-secondary text-secondary-foreground py-12">
			<div class="mx-auto max-w-[1200px] flex flex-col gap-12 px-2">
				<div class="grid lg:grid-cols-2 gap-12">
					<div class="grid sm:grid-cols-2 gap-6">
						<div v-for="link in navigation">
							<NuxtLink v-if="link.path.startsWith('/')" :to="link.path" class="text-isu-yellow! font-bold">{{link.title}}</NuxtLink>
							<a v-else :href="link.path" class="text-isu-yellow! font-bold">{{link.title === "NIDC" ? "The National Indigenous Data Catalogue" : link.title}}</a>
							<div class="flex flex-col">
								<template v-for="child in link.children?.filter(c => c.path !== link.path)">
									<NuxtLink v-if="child.path.startsWith('/')" :to="child.path" class="text-foreground!">{{child.title}}</NuxtLink>
									<a v-else :href="child.path" class="text-foreground!">{{child.title}}</a>
								</template>
							</div>
						</div>
					</div>
					<div class="flex flex-col gap-8">
						<div class="grid grid-cols-[3fr_min-content_2fr] items-center gap-8">
							<a href="https://indigenousdatacommons.org" class="">
								<NuxtImg src="/img/UoM_Indig.Data.Com_Brand_Art_RGB_Logo_White.png" />
							</a>
							<Separator orientation="vertical" class="!h-3/4 bg-muted-foreground" />
							<a href="https://mspgh.unimelb.edu.au/centres-institutes/onemda/research-group/indigenous-studies-unit/indigenous-data-network" class="">
								<NuxtImg src="/img/UoM_Indig_Studies_Unit_Brand_ART - (ICON LOCK UP) IDN - WHITE.png" />
							</a>
						</div>
						<div class="flex flex-row items-center gap-2 justify-between flex-wrap">
							<div class="flex flex-row items-center justify-around gap-2 grow">
								<IDCButton v-for="social in socials" size="icon" variant="green" :title="social.title" asChild>
									<a :href="social.url">
										<FontAwesomeIcon :icon="social.icon" />
									</a>
								</IDCButton>
							</div>
							<IDCButton variant="red" asChild>
								<a href="https://indigenousdatacommons.org/news/newsletter">
									<Newspaper class="size-4" /> Subscribe to our newsletter
								</a>
							</IDCButton>
						</div>
					</div>
				</div>
				<div class="text-center">&copy; Indigenous Data Network 2026</div>
			</div>
		</footer>
	</div>
</template>

<style scoped>
footer {
	background-image: url("/img/conny-schneider-xuTJZ7uD7PI-unsplash.jpg");
	background-repeat: no-repeat;
	background-position-x: right;
	background-position-y: top;
	background-blend-mode: lighten;
	//background-blend-mode: luminosity;
}
</style>