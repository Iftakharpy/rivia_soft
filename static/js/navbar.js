document.addEventListener('DOMContentLoaded', function() {
  const mainNav = document.getElementById('main-nav');
  const secondaryNav = document.getElementById('secondary-nav');
  const mobileMenuButton = document.getElementById('mobile-menu-button');
  const mobileMenuOpenIcon = document.getElementById('mobile-menu-open-icon');
  const mobileMenuCloseIcon = document.getElementById('mobile-menu-close-icon');

  const navLinkTemplate = document.getElementById('nav-link-template');
  const navGroupTemplate = document.getElementById('nav-group-template');
  const secondaryNavItemTemplate = document.getElementById('secondary-nav-item-template');

  function createNavLink(item) {
    const link = navLinkTemplate.content.cloneNode(true).querySelector('[data-link-item]');
    link.href = item.url;
    link.textContent = item.name;
    if (item.extraClassList) {
      link.classList.add(...item.extraClassList);
    }
    return link;
  }

  function createNavGroup(item) {
    const linkGroup = navGroupTemplate.content.cloneNode(true).querySelector('[data-link-group]');
    const groupToggleBtn = linkGroup.querySelector('[data-link-group-btn]');
    const dropdownLinksWrapper = linkGroup.querySelector('[data-links-wrapper]');
    const dropdownLinks = dropdownLinksWrapper.querySelector('[data-links-container]');

    if (item.extraClassList) {
      dropdownLinks.classList.add(...item.extraClassList);
    }

    groupToggleBtn.querySelector('[data-group-name]').textContent = item.groupName;

    item.urls.forEach(subItem => {
      if (subItem.groupName) {
        dropdownLinks.appendChild(createNavGroup(subItem));
      } else {
        dropdownLinks.appendChild(createNavLink(subItem));
      }
    });

    groupToggleBtn.addEventListener('click', (event) => {
      const wasOpen = !dropdownLinksWrapper.classList.contains('hidden');
      // Now, explicitly toggle the current dropdown's state
      if (wasOpen) {
        dropdownLinksWrapper.classList.add('hidden');
        groupToggleBtn.querySelector('svg').classList.remove('rotate-180');
      } else {
        dropdownLinksWrapper.classList.remove('hidden');
        groupToggleBtn.querySelector('svg').classList.add('rotate-180');
      }
      
      // Find all groups that are direct children of the same container (siblings)
      const parentContainer = linkGroup.parentElement;
      const siblingGroups = Array.from(parentContainer.children).filter(child => child.matches('[data-link-group]'));

      // Close the dropdowns of all sibling groups
      siblingGroups.forEach(sibling => {
        if (sibling !== linkGroup) { // Don't close the one we are currently interacting with
          const siblingDropdown = sibling.querySelector('[data-links-wrapper]');
          const siblingButton = sibling.querySelector('[data-link-group-btn]');
          if (siblingDropdown && siblingButton) {
            siblingDropdown.classList.add('hidden');
            siblingButton.querySelector('svg').classList.remove('rotate-180');
          }
        }
      });
    });

    return linkGroup;
  }

  window.NAV_LINKS.primary.forEach(item => {
    if (item.groupName) {
      mainNav.appendChild(createNavGroup(item));
    } else {
      mainNav.appendChild(createNavLink(item));
    }
  });

  window.NAV_LINKS.secondary.forEach(item => {
    const secondaryItem = secondaryNavItemTemplate.content.cloneNode(true);
    const link = secondaryItem.querySelector('a');
    const img = secondaryItem.querySelector('img');
    const tooltip = secondaryItem.querySelector('[data-link-title]');

    link.href = item.url;
    img.src = item.iconImgSrc;
    img.alt = item.name;
    tooltip.textContent = item.name;

    secondaryNav.appendChild(secondaryItem);
  });

  mobileMenuButton.addEventListener('click', () => {
    mainNav.classList.toggle('hidden');
    mobileMenuOpenIcon.classList.toggle('hidden');
    mobileMenuCloseIcon.classList.toggle('hidden');
  });

  document.addEventListener('click', (event) => {
    // Close all dropdowns if the click is outside any nav group
    document.querySelectorAll('[data-link-group]').forEach(group => {
        if (!group.contains(event.target)) {
            const dropdown = group.querySelector('[data-links-wrapper]');
            const button = group.querySelector('[data-link-group-btn]');
            dropdown.classList.add('hidden');
            button.querySelector('svg').classList.remove('rotate-180');
        }
    });
  });
});
