function heuristicParseSFM(text){
  const lines = text.split(/\r?\n/);
  let name = "";
  const tags = new Set();
  const blocks = [];
  const stack = [{blocks: blocks}];
  let activeIO = null;

  function current() { return stack[stack.length - 1]; }

  function parseLocation(io, line) {
    const upper = line.toUpperCase();
    const locMatch = line.match(/^(?:FROM|TO)\b\s*(?:EMPTY\s+SLOTS\s+IN\s+)?(?:EACH\s+)?(.*)$/i);
    if(locMatch){
       if(upper.includes("EMPTY SLOTS IN")) io.emptySlots = true;
       if(upper.includes("EACH")) io.eachLabels = true;
       let rest = locMatch[1] || "";
       const slotsMatch = rest.match(/SLOTS\s+([0-9,-]+)/i);
       if(slotsMatch) { io.slots = slotsMatch[1]; rest = rest.replace(/SLOTS\s+[0-9,-]+/i, "").trim(); }
       const rrMatch = rest.match(/ROUND\s+ROBIN\s+BY\s+(LABEL|BLOCK)/i);
       if(rrMatch){ io.roundRobin = rrMatch[1].toLowerCase(); rest = rest.replace(/ROUND\s+ROBIN\s+BY\s+(LABEL|BLOCK)/i, "").trim(); }
       const sideMatch = rest.match(/(?:(.*)\s+SIDE|EACH\s+SIDE)/i);
       if(sideMatch){
          if(upper.includes("EACH SIDE")) io.sideMode = "each";
          else { io.sideMode = "listed"; io.sides = sideMatch[1].trim(); rest = rest.replace(/(.*)\s+SIDE/i, "").trim(); }
       }
       io.labels = (io.labels ? io.labels + ", " : "") + rest.replace(/,$/,"").trim();
       io.labels = splitLoose(io.labels).join(", ");
       splitLoose(io.labels).forEach(t => tags.add(t));
       return true;
    }
    return false;
  }

  function parseLimitPart(lim, rest) {
    const eachQ = /\bEACH\b/i.test(rest.split(/RETAIN/i)[0]);
    if(eachQ) lim.quantityEach = true;
    const qMatch = rest.match(/^(\d+)/);
    if(qMatch) { lim.quantity = qMatch[1]; rest = rest.replace(/^\d+\s*(?:EACH)?\s*/i, ""); }

    if(/\bRETAIN\b/i.test(rest)){
      const parts = rest.split(/\bRETAIN\b/i);
      if(!lim.quantity) lim.resources = parts[0].trim();
      let rPart = parts[1].trim();
      const eachR = /\bEACH\b/i.test(rPart);
      if(eachR) lim.retainEach = true;
      const rMatch = rPart.match(/^(\d+)/);
      if(rMatch){ lim.retain = rMatch[1]; rPart = rPart.replace(/^\d+\s*(?:EACH)?\s*/i, ""); }
      lim.resources = (lim.resources ? lim.resources + " " : "") + rPart;
    } else { lim.resources = rest.trim(); }

    if(/\b(WITH|WITHOUT)\b/i.test(lim.resources)){
      const wMatch = lim.resources.match(/\b(WITH|WITHOUT)\b\s+(.*)$/i);
      if(wMatch){ lim.withMode = wMatch[1].toLowerCase(); lim.withClause = wMatch[2]; lim.resources = lim.resources.split(/\b(WITH|WITHOUT)\b/i)[0].trim(); }
    }
  }

  for(let line of lines){
    let trimmed = line.trim();
    if(!trimmed) continue;
    const upper = trimmed.toUpperCase();

    const nameMatch = trimmed.match(/^(?:NAME|\{name)\s+"?([^"}]+)"?/i);
    if(nameMatch && stack.length === 1){ name = nameMatch[1]; continue; }

    if(trimmed.startsWith("--")){
      const c = createBlock("comment"); c.value = trimmed.slice(2).trim(); current().blocks.push(c);
      activeIO = null; continue;
    }

    if(upper.startsWith("EVERY ")){
      const t = createBlock("trigger");
      const val = upper.slice(6).replace(" DO","");
      if(val === "REDSTONE PULSE") t.scheduleMode = "redstone";
      else {
        t.scheduleMode = "interval";
        const parts = val.split(/\s+/);
        t.intervalValue = parts.find(p => /^\d+$/.test(p)) || "20";
        t.intervalUnit = parts.find(p => ["TICKS","TICK","SECONDS","SECOND"].includes(p))?.toLowerCase() || "ticks";
        t.intervalGlobal = parts.includes("GLOBAL");
      }
      current().blocks.push(t);
      stack.push({type: "trigger", block: t, blocks: t.children});
      activeIO = null; continue;
    }

    if(upper.startsWith("IF ") || upper.startsWith("ELSE IF ")){
      const isElseIf = upper.startsWith("ELSE IF ");
      const cond = trimmed.replace(/^(?:ELSE IF|IF)\s+/i, "").replace(/\s+THEN$/i, "");
      if(isElseIf && (current().type === "if" || stack[stack.length-2]?.type === "if")){
         if(current().type === "branch") stack.pop();
         const br = makeBranch(cond); current().block.branches.push(br);
         stack.push({type: "branch", blocks: br.blocks});
      } else {
         const i = createBlock("if"); i.branches[0].condition = cond;
         current().blocks.push(i);
         stack.push({type: "if", block: i});
         stack.push({type: "branch", blocks: i.branches[0].blocks});
      }
      activeIO = null; continue;
    }

    if(upper === "ELSE" && (current().type === "if" || stack[stack.length-2]?.type === "if")){
      if(current().type === "branch") stack.pop();
      const i = current().block; i.hasElse = true;
      stack.push({type: "else", blocks: i.elseBlocks});
      activeIO = null; continue;
    }

    if(upper === "END"){
      if(stack.length > 1){
        if(["branch","else"].includes(current().type)) stack.pop();
        stack.pop();
      }
      activeIO = null; continue;
    }

    if(upper.startsWith("FORGET")){
      const f = createBlock("forget"); f.labels = trimmed.slice(6).trim();
      splitLoose(f.labels).forEach(t => tags.add(t));
      current().blocks.push(f); activeIO = null; continue;
    }

    if(upper.startsWith("INPUT") || upper.startsWith("OUTPUT")){
      const type = upper.startsWith("INPUT") ? "input" : "output";
      activeIO = createBlock(type); activeIO.limits = [];
      current().blocks.push(activeIO);
      trimmed = trimmed.slice(6).trim();
      if(!trimmed) continue;
    }

    if(activeIO){
      // Inline check
      const locIdx = upper.indexOf(activeIO.type === "input" ? " FROM " : " TO ");
      if(locIdx !== -1){
        const res = trimmed.slice(0, locIdx).trim();
        const loc = trimmed.slice(locIdx).trim();
        if(res){
           const lim = makeLimit(); parseLimitPart(lim, res.replace(/,$/,""));
           activeIO.limits.push(lim);
        }
        parseLocation(activeIO, loc);
        activeIO = null; continue;
      }

      if(parseLocation(activeIO, trimmed)) continue;

      if(upper.startsWith("EXCEPT")){
        let rest = trimmed.slice(6).trim();
        activeIO.exclusions = (activeIO.exclusions ? activeIO.exclusions + ", " : "") + rest.replace(/,$/,"");
        continue;
      }

      // Resource / Limit line
      const lim = makeLimit();
      parseLimitPart(lim, trimmed.replace(/,$/,""));
      activeIO.limits.push(lim);
      continue;
    }

    const fallback = createBlock("comment"); fallback.value = trimmed;
    current().blocks.push(fallback); activeIO = null;
  }

  walk(blocks, b => { if((b.type === "input" || b.type === "output") && b.limits.length === 0) b.limits.push(makeLimit()); });
  if(!name) name = "Imported Script";
  const s = createScript(name, blocks); s.tags = Array.from(tags);
  return s;
}
