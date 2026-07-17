import tailwindcss from "@tailwindcss/vite";

// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
    compatibilityDate: "2026-01-19",
    devtools: { enabled: true },
    modules: [ "shadcn-nuxt", "@nuxtjs/color-mode", "@nuxt/image"],
    css: [
        "~/assets/css/tailwind.css",
        "~/assets/css/style.css",
    ],
    vite: {
        plugins: [tailwindcss()],
    },
    app: {
        head: {
            link: [
                { rel: "stylesheet", href: "https://fonts.googleapis.com/css2?family=Open+Sans:ital,wght@0,300..800;1,300..800&display=swap", type: "text/css" },
                { rel: "icon", type: "image/png", href: "/favicon-96x96.png", sizes: "96x96" },
                { rel: "icon", type: "image/svg+xml", href: "/favicon.svg" },
                { rel: "shortcut icon", href: "/favicon.ico" },
                { rel: "apple-touch-icon", sizes: "180x180", href: "/apple-touch-icon.png" },
                { rel: "manifest", href: "/site.webmanifest" },
            ],
            meta: [
                { name: "apple-mobile-web-app-title", content: "IDN Catalogue Profile" },
            ],
            title: "IDN Catalogue Profile",
        },
    },
    colorMode: {
        classPrefix: "",
        classSuffix: "",
    },
    nitro: {
        prerender: {
            autoSubfolderIndex: false,
        },
    },
    shadcn: {
        prefix: "",
        componentDir: "./app/components/ui"
    },
    image: {
        provider: "none",
    },
});