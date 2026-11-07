-- Keep chapter files independent; build the five approved parts in every format.
local parts = {
  [1] = 'Часть I. Республика на пороге перемен',
  [4] = 'Часть II. Восхождение Цезаря',
  [8] = 'Часть III. Наследник',
  [11] = 'Часть IV. Август и создание принципата',
  [15] = 'Часть V. Историческое сравнение'
}
function Header(h)
  local original = h.level
  h.level = original + 1
  if original == 1 then
    local number = tonumber(pandoc.utils.stringify(h.content):match('^Глава (%d+)%.'))
    if number and parts[number] then
      local part = pandoc.Header(1, parts[number], pandoc.Attr('part' .. number))
      return {part, h}
    end
  end
  return h
end
