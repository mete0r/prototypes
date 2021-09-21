/**!
 * METE0R-PROJECT: SOME_DESCRIPTION
 * Copyright (C) 2015-2021 Yoosung Moon <yoosungmoon@naver.com>
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Affero General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Affero General Public License for more details.
 *
 * You should have received a copy of the GNU Affero General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 *
 * root.js
 *
 */
import { Tooltip } from 'bootstrap';

document.addEventListener("DOMContentLoaded", () => {
    const main = document.querySelector('main');
    main.classList.add("h1");

    const tooltipList = document.querySelectorAll(
        '[data-bs-toggle="tooltip"]'
    );
    tooltipList.forEach(el => new Tooltip(el));
});
