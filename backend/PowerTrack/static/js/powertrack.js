document.addEventListener("DOMContentLoaded", () => {

    /*
     * =====================================================
     * SIDEBAR
     * =====================================================
     */

    const body = document.body;

    const sidebar = document.getElementById("powerSidebar");
    const overlay = document.getElementById("sidebarOverlay");

    const openButton = document.getElementById("openSidebar");
    const closeButton = document.getElementById("closeSidebar");


    function openSidebar() {
        if (!sidebar) return;

        body.classList.add("sidebar-open");
    }


    function closeSidebar() {
        body.classList.remove("sidebar-open");
    }


    if (openButton) {
        openButton.addEventListener("click", openSidebar);
    }


    if (closeButton) {
        closeButton.addEventListener("click", closeSidebar);
    }


    if (overlay) {
        overlay.addEventListener("click", closeSidebar);
    }


    /*
     * Close mobile navigation after selecting a page.
     */

    document.querySelectorAll(".sidebar-nav .nav-item").forEach((item) => {

        item.addEventListener("click", () => {

            if (window.innerWidth <= 850) {
                closeSidebar();
            }

        });

    });


    /*
     * =====================================================
     * ACTIVE NAVIGATION
     * =====================================================
     */

    const currentPath = window.location.pathname.replace(/\/+$/, "");

    document.querySelectorAll(".sidebar-nav .nav-item").forEach((item) => {

        const link = item.getAttribute("href");

        if (!link || link.startsWith("#")) {
            return;
        }

        try {

            const linkUrl = new URL(link, window.location.origin);

            const linkPath = linkUrl.pathname.replace(/\/+$/, "");

            if (
                linkPath === currentPath ||
                (
                    linkPath !== "/" &&
                    currentPath.startsWith(linkPath + "/")
                )
            ) {
                item.classList.add("active");
            }

        } catch (error) {
            console.warn("PowerTrack navigation error:", error);
        }

    });


    /*
     * =====================================================
     * DASHBOARD PERIOD BUTTONS
     * =====================================================
     */

    document.querySelectorAll(".chart-range").forEach((button) => {

        button.addEventListener("click", () => {

            document
                .querySelectorAll(".chart-range")
                .forEach((item) => item.classList.remove("active"));

            button.classList.add("active");

        });

    });


    /*
     * =====================================================
     * ESCAPE KEY
     * =====================================================
     */

    document.addEventListener("keydown", (event) => {

        if (event.key === "Escape") {
            closeSidebar();
        }

    });

});
